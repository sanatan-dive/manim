"""In-memory job storage for Phase 2."""
from typing import Dict, Optional
from datetime import datetime
import uuid
from collections import OrderedDict
from app.models.job import Job, JobStatus
from config import settings


class JobStore:
    """Thread-safe in-memory job storage."""
    
    def __init__(self, max_jobs: int = 100):
        self._jobs: OrderedDict[str, Job] = OrderedDict()
        self._max_jobs = max_jobs
    
    def create_job(self, prompt: str) -> Job:
        """Create a new job with PENDING status."""
        job_id = str(uuid.uuid4())
        now = datetime.now()
        
        job = Job(
            job_id=job_id,
            prompt=prompt,
            status=JobStatus.PENDING,
            created_at=now,
            updated_at=now
        )
        
        self._jobs[job_id] = job
        
        # Remove oldest jobs if we exceed max
        if len(self._jobs) > self._max_jobs:
            self._jobs.popitem(last=False)
        
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        code: Optional[str] = None,
        video_url: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_log: Optional[str] = None
    ) -> Optional[Job]:
        """Update a job's fields."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        if status is not None:
            job.status = status
        if code is not None:
            job.code = code
        if video_url is not None:
            job.video_url = video_url
        if error_message is not None:
            job.error_message = error_message
        if execution_log is not None:
            job.execution_log = execution_log
        
        job.updated_at = datetime.now()
        return job
    
    def list_jobs(self, limit: int = 50) -> list[Job]:
        """List recent jobs."""
        jobs = list(self._jobs.values())
        return jobs[-limit:][::-1]  # Most recent first


# Global job store instance
job_store = JobStore(max_jobs=settings.MAX_JOB_HISTORY)
