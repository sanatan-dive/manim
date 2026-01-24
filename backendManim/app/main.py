from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)

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
    prompt: str = Field(..., min_length=10, max_length=1000, description="The animation description")
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
async def generate_animation(
    request: Request, 
    body: GenerateRequest, 
    current_user = Depends(get_current_active_user),
    x_gemini_api_key: Optional[str] = Header(None, alias="x-gemini-api-key")
):
    """Queue animation generation task."""
    try:
        # 1. Check concurrent jobs FIRST
        active_jobs = await db_service.count_active_jobs(current_user.id)
        if active_jobs >= settings.MAX_CONCURRENT_JOBS:
            raise HTTPException(
                status_code=429, 
                detail=f"You have reached the maximum number of concurrent jobs ({settings.MAX_CONCURRENT_JOBS}). Please wait for one to finish."
            )

        # 2. Check Credits & API Key
        user_api_key = None
        
        if current_user.credits > 0:
            # User has credits
            await db_service.deduct_credit(current_user.id)
            logger.info(f"Deducted 1 credit from user {current_user.id}. Remaining: {current_user.credits - 1}")
        else:
            # No credits, must use API Key
            if not x_gemini_api_key:
                raise HTTPException(
                    status_code=402, # Payment Required signal
                    detail="Zero credits"
                )
            user_api_key = x_gemini_api_key
            logger.info(f"User {current_user.id} using custom API Key.")
            # We still want to track usage count? Yes.
            await db_service.increment_usage(current_user.id)

        # Import the task here to avoid circular imports
        from app.tasks import process_animation_job
        
        # Queue the task with the prompt
        task = process_animation_job.apply_async(
            args=[body.prompt, user_api_key],
            time_limit=settings.JOB_TIMEOUT,
            soft_time_limit=settings.JOB_SOFT_TIMEOUT
        )

        await db_service.create_job(
            job_id=task.id, 
            prompt=body.prompt, 
            user_id=current_user.id,
            conversation_id=body.conversation_id
        )
        
        # We handled credit deduction logic above? No I need to implement it correctly.
        # Let's replace the whole function body in one go.
        
        logger.info(f"[Task {task.id}] Created for prompt: {body.prompt[:50]}... User: {current_user.id}")
        
        return GenerateResponse(
            job_id=task.id,
            status="pending",
            message="Job queued for processing"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (from 402 or 429)
        raise
    except Exception as e:
        logger.error(f"Failed to queue task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str, request: Request):
    """Check Celery task status."""
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Construct video URL to go through our proxy/redirect endpoint
    # This ensures fresh signatures and valid range requests
    video_url = job.get('videoUrl')
    if video_url and job.get('status') == 'completed':
        # Use the stream endpoint which handles redirects/refreshing
        video_url = str(request.url_for('stream_video', job_id=job['id']))

    return {
        "job_id": job['id'],
        "status": job['status'],
        "code": job.get('generatedCode'),
        "video_url": video_url,
        "error_message": job.get('errorMessage'),
        "execution_log": job.get('executionLog'),
        "created_at": job['createdAt'].isoformat(),
        "updated_at": job['updatedAt'].isoformat()
    }

@app.get("/video/stream/{job_id}")
async def stream_video(job_id: str):
    """Redirect to video stream from S3 or serve local."""
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Check for S3 Key first
    s3_key = job.get('s3Key')
    
    # If S3 is enabled and we have a key
    if s3_service.enabled and s3_key:
        try:
            # Generate a FRESH presigned URL (solves expiry) without ResponseContentType to let S3 default or set it
            # Explicitly set Content-Type to video/mp4 to ensure browser treats it as video
            url = s3_service.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_S3_BUCKET,
                    'Key': s3_key,
                    'ResponseContentType': 'video/mp4'
                },
                ExpiresIn=3600 # 1 hour validity for this specific view
            )
            from fastapi.responses import RedirectResponse
            # Using 307 Temporary Redirect to preserve method and body if any, but mostly for semantics
            return RedirectResponse(url=url)
        except Exception as e:
            logger.error(f"Failed to generate redirect URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to access video")

    # Fallback/Local logic
    video_url = job.get('videoUrl')
    if not video_url:
        raise HTTPException(status_code=404, detail="Video URL not found")

    # If it's a local path (starts with /videos/)
    if video_url.startswith('/videos/'):
         from fastapi.responses import RedirectResponse
         return RedirectResponse(url=video_url)

    # If it's already an HTTP URL (legacy S3 or external)
    if video_url.startswith('http'):
         from fastapi.responses import RedirectResponse
         return RedirectResponse(url=video_url)
    
    raise HTTPException(status_code=404, detail="Video not accessible")




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