"""Celery tasks for animation generation."""
import logging
from app.celery_app import celery_app
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

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_animation_job")
def process_animation_job(self, prompt: str):
    """
    Celery task to process animation generation.
    
    Args:
        self: Celery task instance
        prompt: User's text prompt for animation
        
    Returns:
        dict: Contains video_url and execution_log
    """
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Starting processing for prompt: {prompt[:50]}...")
    
    try:
        # Update task state: Generating code
        self.update_state(state='GENERATING_CODE', meta={'progress': 'Generating code with AI'})
        logger.info(f"[Task {task_id}] Generating code...")
        
        # Generate code using AI
        code = generate_code(prompt)
        save_code(code)
        logger.info(f"[Task {task_id}] Code generated successfully")
        
        # Update task state: Rendering
        self.update_state(state='RENDERING', meta={'progress': 'Rendering animation with Manim'})
        logger.info(f"[Task {task_id}] Rendering animation...")
        
        # Execute Manim
        stdout, stderr = execute_manim()
        video_url = get_video_url()
        
        logger.info(f"[Task {task_id}] Completed successfully!")
        
        return {
            'status': 'completed',
            'video_url': video_url,
            'execution_log': f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        }
        
    except SecurityViolationError as e:
        logger.error(f"[Task {task_id}] Security violation: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Security violation: {str(e)}'}
        )
        raise
        
    except CodeGenerationError as e:
        logger.error(f"[Task {task_id}] Code generation failed: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Code generation failed: {str(e)}'}
        )
        raise
        
    except RenderError as e:
        logger.error(f"[Task {task_id}] Rendering failed: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Rendering failed: {str(e)}'}
        )
        raise
        
    except Exception as e:
        logger.error(f"[Task {task_id}] Unexpected error: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': f'Unexpected error: {str(e)}'}
        )
        raise
