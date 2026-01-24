import logging
from app.celery_app import celery_app
from app.services.ai_service import (
    generate_code, save_code, fix_code,
    CodeGenerationError, SecurityViolationError, MAX_RETRY_ATTEMPTS
)
from app.services.render_service import execute_manim, get_video_url, RenderError, extract_error_details
from app.services.database_service import db_service
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions in sync Celery tasks."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(coro)


async def process_job_async(task_id: str, prompt: str, self_task, api_key: str = None):
    """Async handler for the animation job with self-healing retry mechanism."""
    code = None
    last_error = None
    
    try:
        # Connect to DB locally for this task
        await db_service.connect()
        
        # Update status: Generating code
        self_task.update_state(state='GENERATING_CODE')
        await db_service.update_job_status(task_id, 'generating_code')
        logger.info(f"[Task {task_id}] Generating code...")
        
        # Generate initial code
        code = generate_code(prompt, api_key)
        save_code(code)
        logger.info(f"[Task {task_id}] Code generated successfully")
        
        # Attempt rendering with retry loop
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                # Update status: Rendering
                self_task.update_state(state='RENDERING', meta={'attempt': attempt})
                status_msg = f'rendering' if attempt == 1 else f'rendering (retry {attempt}/{MAX_RETRY_ATTEMPTS})'
                await db_service.update_job_status(task_id, status_msg)
                logger.info(f"[Task {task_id}] Rendering animation (attempt {attempt}/{MAX_RETRY_ATTEMPTS})...")
                
                # Execute Manim
                stdout, stderr = execute_manim()
                
                # If we get here, rendering succeeded!
                video_url = get_video_url()
                execution_log = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                if attempt > 1:
                    execution_log = f"Successfully rendered after {attempt} attempts.\n\n{execution_log}"
                
                # Extract S3 key (only if S3 is enabled)
                s3_key = _extract_s3_key(video_url)
                
                # Update result
                await db_service.update_job_result(
                    job_id=task_id,
                    video_url=video_url,
                    execution_log=execution_log,
                    generated_code=code,
                    s3_key=s3_key
                )
                
                logger.info(f"[Task {task_id}] Completed successfully! Video: {video_url}")
                return {
                    'status': 'completed',
                    'video_url': video_url,
                    'execution_log': execution_log,
                    'attempts': attempt
                }
                
            except RenderError as render_error:
                last_error = render_error
                error_details = extract_error_details(render_error.stderr)
                logger.warning(f"[Task {task_id}] Render attempt {attempt} failed: {error_details[:200]}...")
                
                # Check if we have more attempts
                if attempt < MAX_RETRY_ATTEMPTS:
                    # Try to fix the code
                    self_task.update_state(state='FIXING_CODE', meta={'attempt': attempt})
                    await db_service.update_job_status(task_id, f'fixing_code (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})')
                    logger.info(f"[Task {task_id}] Attempting to fix code...")
                    
                    try:
                        # Get the failed code
                        failed_code = render_error.code if render_error.code else code
                        
                        # Ask AI to fix the code
                        code = fix_code(
                            original_prompt=prompt,
                            failed_code=failed_code,
                            error_message=error_details,
                            attempt=attempt + 1,
                            api_key=api_key
                        )
                        save_code(code)
                        logger.info(f"[Task {task_id}] Fixed code saved, retrying render...")
                        
                    except (CodeGenerationError, SecurityViolationError) as fix_error:
                        logger.error(f"[Task {task_id}] Failed to fix code: {fix_error}")
                        # Continue to next attempt anyway with same code
                        continue
                else:
                    # Out of retries
                    logger.error(f"[Task {task_id}] All {MAX_RETRY_ATTEMPTS} render attempts failed")
                    raise
        
        # Should not reach here, but just in case
        raise last_error if last_error else RenderError("Unknown rendering error")
        
    except Exception as e:
        # Re-raise to be caught in main task
        raise e
    finally:
        # Always disconnect
        await db_service.disconnect()


def _extract_s3_key(video_url: str) -> str | None:
    """Extract S3 key from video URL if S3 storage is enabled."""
    if settings.STORAGE_MODE != "s3":
        return None
        
    if not video_url or not video_url.startswith("https://"):
        if video_url and "/videos/" in video_url:
            s3_key = video_url.split("/videos/", 1)[-1]
            if s3_key and not s3_key.startswith("videos/"):
                s3_key = f"videos/{s3_key}"
            return s3_key
        return None
    
    try:
        from urllib.parse import urlparse
        path = urlparse(video_url).path
        return path.lstrip('/')
    except:
        if "/videos/" in video_url:
            s3_key = video_url.split("/videos/", 1)[-1]
            if s3_key and not s3_key.startswith("videos/"):
                s3_key = f"videos/{s3_key}"
            return s3_key
        return None


@celery_app.task(bind=True, name="process_animation_job")
def process_animation_job(self, prompt: str, api_key: str = None):
    """Celery task entry point."""
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Starting processing for prompt: {prompt[:50]}...")
    
    try:
        return run_async(process_job_async(task_id, prompt, self, api_key))
        
    except SecurityViolationError as e:
        logger.error(f"[Task {task_id}] Security violation: {str(e)}")
        run_async(db_service.connect())
        run_async(db_service.update_job_error(task_id, f"Security violation: {str(e)}"))
        run_async(db_service.disconnect())
        raise
        
    except CodeGenerationError as e:
        logger.error(f"[Task {task_id}] Code generation failed: {str(e)}")
        run_async(db_service.connect())
        run_async(db_service.update_job_error(task_id, f"Code generation failed: {str(e)}"))
        run_async(db_service.disconnect())
        raise
        
    except RenderError as e:
        logger.error(f"[Task {task_id}] Rendering failed: {str(e)}")
        run_async(db_service.connect())
        run_async(db_service.update_job_error(task_id, f"Rendering failed: {str(e)}"))
        run_async(db_service.disconnect())
        raise
        
    except Exception as e:
        logger.error(f"[Task {task_id}] Unexpected error: {str(e)}")
        # Try to log error to DB if possible
        try:
            run_async(db_service.connect())
            run_async(db_service.update_job_error(task_id, f"Unexpected error: {str(e)}"))
            run_async(db_service.disconnect())
        except Exception as db_err:
            logger.error(f"Failed to log error to DB: {str(db_err)}")
        raise