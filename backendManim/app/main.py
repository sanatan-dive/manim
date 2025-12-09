from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from pathlib import Path
from config import settings
from app.models.job import Job, JobStatus
from app.services.job_store import job_store
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Manim Animation Generator", 
    version="3.0.0",
    description="Generate Manim animations from text prompts using AI with Celery"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video serving
app.mount("/videos", StaticFiles(directory="media/videos"), name="videos")


class GenerateRequest(BaseModel):
    """Request model for animation generation."""
    prompt: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a circle that transforms into a square"
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
async def generate_animation(request: GenerateRequest):
    """Queue animation generation task."""
    try:
        # Import the task here to avoid circular imports
        from app.tasks import process_animation_job
        
        # Queue the task with the prompt
        task = process_animation_job.delay(request.prompt)
        
        logger.info(f"[Task {task.id}] Created for prompt: {request.prompt[:50]}...")
        
        return GenerateResponse(
            job_id=task.id,
            status="pending",
            message="Job queued for processing"
        )
        
    except Exception as e:
        logger.error(f"Failed to queue task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check Celery task status."""
    task = celery_app.AsyncResult(job_id)
    
    response = {
        "job_id": job_id,
        "status": task.state.lower()
    }
    
    if task.state == 'PENDING':
        response['message'] = 'Task is waiting to be processed'
    elif task.state == 'GENERATING_CODE':
        response['message'] = 'Generating animation code with AI'
    elif task.state == 'RENDERING':
        response['message'] = 'Rendering animation with Manim'
    elif task.state == 'SUCCESS':
        result = task.result
        response['status'] = 'completed'
        response['video_url'] = result.get('video_url')
        response['execution_log'] = result.get('execution_log')
    elif task.state == 'FAILURE':
        response['status'] = 'failed'
        response['error_message'] = str(task.info)
    else:
        response['message'] = f'Task state: {task.state}'
    
    return response

@app.get("/jobs")
async def list_jobs(limit: int = 20):
    """List recent jobs from Celery."""
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    # For now, return empty list since we need to configure result backend properly
    # In production, you'd query Celery's result backend
    return {
        "jobs": [],
        "count": 0,
        "message": "Job history requires result backend configuration"
    }