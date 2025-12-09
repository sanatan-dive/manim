"""Celery app configuration."""
from celery import Celery
from config import settings

# Create Celery instance
celery_app = Celery(
    "manim_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks']  
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  
)
