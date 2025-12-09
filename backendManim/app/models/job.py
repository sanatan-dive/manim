from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    """Status of a generation job."""
    PENDING = "pending"
    GENERATING_CODE = "generating_code"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Model for tracking animation generation jobs."""
    job_id: str
    prompt: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    code: Optional[str] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    execution_log: Optional[str] = None
    
    class Config:
        use_enum_values = True
