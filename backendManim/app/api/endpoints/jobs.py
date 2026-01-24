from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_active_user
from app.services.database_service import db_service
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

class JobResponse(BaseModel):
    id: str
    title: Optional[str] = None
    prompt: str
    status: str
    videoUrl: Optional[str] = None
    code: Optional[str] = Field(None, alias="generatedCode")
    duration: Optional[float] = None
    errorMessage: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class PaginatedJobsResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int

@router.get("/public", response_model=PaginatedJobsResponse)
async def list_public_jobs(
    limit: int = Query(20, le=100),
    offset: int = 0,
    search: Optional[str] = None
):
    """
    List public completed jobs (Gallery).
    """
    jobs = await db_service.list_jobs(
        limit=limit, 
        offset=offset, 
        search=search,
        status="completed"
    )
    
    total = await db_service.count_jobs(
        search=search,
        status="completed"
    )
    
    return {
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/", response_model=PaginatedJobsResponse)
async def list_jobs(
    limit: int = Query(20, le=100),
    offset: int = 0,
    search: Optional[str] = None,
    current_user = Depends(get_current_active_user)
):
    """
    List user's jobs with filtering.
    """
    jobs = await db_service.list_jobs(
        limit=limit, 
        offset=offset, 
        user_id=current_user.id,
        search=search
    )
    
    total = await db_service.count_jobs(
        user_id=current_user.id,
        search=search
    )
    
    return {
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific job.
    """
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Ownership check
    if job.get('userId') != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to view this job")
         
    return job

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Delete a job.
    """
    print(f"DEBUG: Attempting to delete job {job_id} for user {current_user.id}")
    
    # Check existence irrespective of user first
    existing_job = await db_service.get_job(job_id)
    if existing_job:
        print(f"DEBUG: Found job {job_id}. Owner: {existing_job.get('userId')}, Status: {existing_job.get('status')}")
    else:
        print(f"DEBUG: Job {job_id} NOT FOUND in DB.")

    deleted_job = await db_service.delete_job(job_id, user_id=current_user.id)
    if not deleted_job:
        print(f"DEBUG: Delete failed. Matches: Job={job_id}, User={current_user.id}")
        raise HTTPException(status_code=404, detail="Job not found or not authorized")
    
    return {"message": "Job deleted successfully", "id": job_id}
