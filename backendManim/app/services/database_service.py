from prisma import Prisma
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db = Prisma()
        self._connected = False

    async def connect(self):
        if not self._connected:
            await self.db.connect()
            self._connected = True
            logger.info("Connected to the database.")

    async def disconnect(self):
        if self._connected:
            await self.db.disconnect()
            self._connected = False
            logger.info("Disconnected from the database.")

    async def create_job(self, job_id:str, prompt:str, )-> dict:
        job = await self.db.job.create(
            data = {
                'id': job_id,
                'prompt': prompt,
                'status': 'PENDING',
            }
        )
        return job.dict()
    
    async def get_job(self, job_id: str) -> Optional[dict]:
        job = await self.db.job.find_unique(
            where = {
                'id': job_id
            }
        )
        if job:
            return job.dict()
        return None
    
    async def update_job_status(self, job_id: str, status: str) -> dict:
        """Update job status."""
        job = await self.db.job.update(
            where={'id': job_id},
            data={
                'status': status,
                'updatedAt': datetime.utcnow()
            }
        )
        return job.dict()
    
    async def update_job_result(
        self, 
        job_id: str, 
        video_url: str, 
        execution_log: str,
        generated_code: Optional[str] = None,
        s3_key: Optional[str] = None
    ) -> dict:
        """Update job with results."""
        job = await self.db.job.update(
            where={'id': job_id},
            data={
                'status': 'completed',
                'videoUrl': video_url,
                's3Key': s3_key,
                'executionLog': execution_log,
                'generatedCode': generated_code,
                'updatedAt': datetime.utcnow()
            }
        )
        return job.dict()
    
    async def update_job_error(self, job_id: str, error_message: str) -> dict:
        """Update job with error."""
        job = await self.db.job.update(
            where={'id': job_id},
            data={
                'status': 'failed',
                'errorMessage': error_message,
                'updatedAt': datetime.utcnow()
            }
        )
        return job.dict()
    

    async def list_jobs(self, limit: int = 20, offset: int = 0) -> List[dict]:
        """List recent jobs."""
        jobs = await self.db.job.find_many(
            take=limit,
            skip=offset,
            order={'createdAt': 'desc'}
        )
        return [job.dict() for job in jobs]
    
    async def count_jobs(self, status: Optional[str] = None) -> int:
        """Count jobs by status."""
        where = {'status': status} if status else {}
        return await self.db.job.count(where=where)
    
    async def delete_old_jobs(self, days: int = 30) -> int:
        """Delete jobs older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.job.delete_many(
            where={'createdAt': {'lt': cutoff_date}}
        )
        return result
    
db_service = DatabaseService()
