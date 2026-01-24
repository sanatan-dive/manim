from prisma import Prisma
from typing import Optional, List
from datetime import datetime, timedelta
import logging
from app.services.s3_service import s3_service

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db = Prisma()
        self.prisma = self.db
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

    async def create_job(self, job_id:str, prompt:str, user_id: Optional[str] = None, conversation_id: Optional[str] = None) -> dict:
        data = {
            'id': job_id,
            'prompt': prompt,
            'status': 'PENDING',
        }
        if user_id:
            data['userId'] = user_id
        
        if conversation_id:
            data['conversationId'] = conversation_id
            
        job = await self.db.job.create(data=data)
        return job.dict()
    
    async def create_conversation(self, user_id: str, title: str) -> dict:
        """Create a new conversation."""
        conversation = await self.db.conversation.create(
            data={
                'userId': user_id,
                'title': title
            }
        )
        return conversation.dict()

    async def list_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """List user conversations."""
        conversations = await self.db.conversation.find_many(
            where={'userId': user_id},
            take=limit,
            skip=offset,
            order={'updatedAt': 'desc'},
            include={'jobs': False} # Do not include jobs in list view for performance
        )
        return [c.dict() for c in conversations]

    async def get_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Get conversation with jobs."""
        where = {'id': conversation_id}
        if user_id:
            where['userId'] = user_id
            
        conversation = await self.db.conversation.find_first(
            where=where,
            include={'jobs': {'order_by': {'createdAt': 'asc'}}}
        )
        
        if conversation:
            return conversation.dict()
        return None

    async def delete_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Delete a conversation and associated S3 files."""
        where = {'id': conversation_id}
        if user_id:
            where['userId'] = user_id
            
        # Check existence and fetch jobs to clean up files
        conv = await self.db.conversation.find_first(
            where=where,
            include={'jobs': True}
        )
        
        if not conv:
            return None
        
        # Cleanup S3 files for all jobs in this conversation
        if conv.jobs:
            for job in conv.jobs:
                if job.s3Key:
                    try:
                        s3_service.delete_video(job.s3Key)
                    except Exception as e:
                        logger.error(f"Failed to delete S3 file for job {job.id}: {e}")
            
        await self.db.conversation.delete(where={'id': conversation_id})
        return conv.dict()

    async def update_conversation(self, conversation_id: str, title: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Update a conversation title."""
        where = {'id': conversation_id}
        if user_id:
            where['userId'] = user_id

        # Check existence
        conv = await self.db.conversation.find_first(where=where)
        if not conv:
            return None

        updated = await self.db.conversation.update(
            where={'id': conversation_id},
            data={'title': title, 'updatedAt': datetime.utcnow()}
        )
        return updated.dict()

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

    async def count_active_jobs(self, user_id: str) -> int:
        """Count jobs that are pending, code_generation, or rendering."""
        active_statuses = ['pending', 'generating_code', 'rendering', 'fixing_code']
        
        return await self.db.job.count(
            where={
                'userId': user_id,
                'status': {'in': active_statuses}
            }
        )
    

    async def list_jobs(self, limit: int = 20, offset: int = 0, user_id: Optional[str] = None, search: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        """List recent jobs with optional filtering."""
        where = {}
        if user_id:
            where['userId'] = user_id
        
        if status:
            where['status'] = status
        
        if search:
            where['OR'] = [
                {'prompt': {'contains': search, 'mode': 'insensitive'}},
                {'title': {'contains': search, 'mode': 'insensitive'}}
            ]

        jobs = await self.db.job.find_many(
            take=limit,
            skip=offset,
            where=where,
            order={'createdAt': 'desc'}
        )
        return [job.dict() for job in jobs]

    async def delete_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Delete a job and its S3 file. If user_id is provided, ensures ownership."""
        where = {'id': job_id}
        if user_id:
            where['userId'] = user_id

        # First check existence
        job = await self.db.job.find_first(where=where)
        if not job:
            return None

        # Delete from S3 if key exists
        if job.s3Key:
            try:
                s3_service.delete_video(job.s3Key)
            except Exception as e:
                logger.error(f"Failed to delete S3 file for job {job_id}: {e}")

        # Delete
        await self.db.job.delete(where={'id': job_id})
        return job.dict()
    
    async def count_jobs(self, user_id: Optional[str] = None, search: Optional[str] = None, status: Optional[str] = None) -> int:
        """Count jobs with filters."""
        where = {}
        if user_id:
            where['userId'] = user_id
        if status:
            where['status'] = status
        
        if search:
            where['OR'] = [
                {'prompt': {'contains': search, 'mode': 'insensitive'}},
                {'title': {'contains': search, 'mode': 'insensitive'}}
            ]
            
        return await self.db.job.count(where=where)
    
    async def delete_old_jobs(self, days: int = 30) -> int:
        """Delete jobs older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.job.delete_many(
            where={'createdAt': {'lt': cutoff_date}}
        )
        return result

    async def increment_usage(self, user_id: str):
        """Increment generation count for user."""
        await self.db.user.update(
            where={'id': user_id},
            data={
                'generationCount': {'increment': 1}
            }
        )

    async def deduct_credit(self, user_id: str, amount: int = 1):
        """Deduct credits from user and increment generation count."""
        await self.db.user.update(
            where={'id': user_id},
            data={
                'credits': {'decrement': amount},
                'generationCount': {'increment': 1}
            }
        )

db_service = DatabaseService()
