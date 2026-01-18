from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from pathlib import Path
from config import settings
from app.models.job import Job, JobStatus
from app.services.job_store import job_store
from app.services.database_service import db_service
from app.services.s3_service import s3_service
from app.services.ai_service import (
    generate_code, 
    save_code, 
    CodeGenerationError, 
    SecurityViolationError
)
from app.services.render_service import (
    execute_manim, 
    get_video_url, 
    RenderError
)
from app.celery_app import celery_app
from app.api.endpoints import users, jobs, conversations
from app.core.security import get_current_active_user
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Manim Animation Generator", 
    version="3.0.0",
    description="Generate Manim animations from text prompts using AI with Celery"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user routes
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# Mount static files for video serving
app.mount("/videos", StaticFiles(directory="media/videos"), name="videos")

@app.on_event("startup")
async def startup_event():
    await db_service.connect()
    logger.info("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    await db_service.disconnect()
    logger.info("Application shutdown complete.")


class GenerateRequest(BaseModel):
    """Request model for animation generation."""
    prompt: str
    conversation_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a circle that transforms into a square",
                "conversation_id": "optional-uuid"
            }
        }


class GenerateResponse(BaseModel):
    """Response model for animation generation."""
    job_id: str
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Manim Animation Generation API",
        "version": "3.0.0",
        "endpoints": {
            "/health": "Health check (GET)",
            "/generate": "Generate animation (POST)",
            "/status/{job_id}": "Check job status (GET)",
            "/jobs": "List recent jobs (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_configured": settings.validate_api_key(),
        "model": settings.MODEL_NAME,
        "redis_url": settings.REDIS_URL,
        "version": "3.0.0"
    }


@app.post("/generate", response_model=GenerateResponse)
@limiter.limit("5/minute")
async def generate_animation(request: Request, body: GenerateRequest, current_user = Depends(get_current_active_user)):
    """Queue animation generation task."""
    try:
        # Import the task here to avoid circular imports
        from app.tasks import process_animation_job
        
        # Queue the task with the prompt
        task = process_animation_job.delay(body.prompt)

        await db_service.create_job(
            job_id=task.id, 
            prompt=body.prompt, 
            user_id=current_user.id,
            conversation_id=body.conversation_id
        )
        
        # Record usage
        await db_service.increment_usage(current_user.id)
        
        logger.info(f"[Task {task.id}] Created for prompt: {body.prompt[:50]}... User: {current_user.id}")
        
        return GenerateResponse(
            job_id=task.id,
            status="pending",
            message="Job queued for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check Celery task status."""
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
     
    return {
        "job_id": job['id'],
        "status": job['status'],
        "video_url": job.get('videoUrl'),
        "error_message": job.get('errorMessage'),
        "execution_log": job.get('executionLog'),
        "created_at": job['createdAt'].isoformat(),
        "updated_at": job['updatedAt'].isoformat()
    }

@app.get("/video/stream/{job_id}")
async def stream_video(job_id: str):
    """Proxy video stream from S3."""
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed")
        
    s3_key = job.get('s3Key')
    
    # If S3 is not enabled, ignore s3_key (force local fallback)
    if not s3_service.enabled:
        s3_key = None

    if not s3_key:
        # Fallback to local if no S3 key but videoUrl exists
        video_url = job.get('videoUrl')
        if video_url:
             if not video_url.startswith('http'):
                 # Local file
                 from fastapi.responses import RedirectResponse
                 return RedirectResponse(video_url)
             
             # If it's a full URL (legacy or s3 url in db), try to extract key
             try:
                 from urllib.parse import urlparse
                 path = urlparse(video_url).path
                 s3_key = path.lstrip('/')
             except:
                pass
        
        if not s3_key:
             raise HTTPException(status_code=404, detail="Video key not found")
        
    try:
        if not s3_service.enabled:
             raise HTTPException(status_code=500, detail="S3 not enabled")

        logger.info(f"Streaming video from S3 using key: {s3_key} from bucket {settings.AWS_S3_BUCKET}")

        # Get object from S3
        file_obj = s3_service.s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key
        )
        
        return StreamingResponse(
            file_obj['Body'],
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"inline; filename=animation_{job_id}.mp4"
            }
        )
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream video")




@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    total_jobs = await db_service.count_jobs()
    pending_jobs = await db_service.count_jobs(status='pending')
    completed_jobs = await db_service.count_jobs(status='completed')
    failed_jobs = await db_service.count_jobs(status='failed')
    
    return {
        "total_jobs": total_jobs,
        "pending": pending_jobs,
        "completed": completed_jobs,
        "failed": failed_jobs,
        "success_rate": round((completed_jobs / total_jobs * 100) if total_jobs > 0 else 0, 2)
    }