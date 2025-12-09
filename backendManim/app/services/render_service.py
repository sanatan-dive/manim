"""Manim rendering service with error handling."""
import subprocess
import sys
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Raised when rendering fails."""
    pass


def execute_manim(filename: Path = None) -> tuple[str, str]:
    """
    Execute Manim to render animation.
    
    Args:
        filename: Path to Python file containing animation code
        
    Returns:
        Tuple of (stdout, stderr)
        
    Raises:
        RenderError: If rendering fails
    """
    if filename is None:
        filename = settings.generated_animation_file
    
    # Ensure file exists
    if not Path(filename).exists():
        raise RenderError(f"Animation file not found: {filename}")
    
    filename = str(filename)
    
    command = [
        sys.executable, "-m", "manim", 
        filename, 
        settings.animation_class_name, 
        settings.manim_quality, 
        "-o", settings.output_video_file
    ]
    
    try:
        logger.info(f"Starting Manim render: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=settings.manim_timeout
        )
        
        logger.info("Manim execution successful")
        logger.debug(f"Manim stdout: {result.stdout}")
        
        return result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"Manim execution timed out after {settings.manim_timeout} seconds"
        logger.error(error_msg)
        raise RenderError(error_msg)
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Manim execution failed with exit code {e.returncode}"
        logger.error(f"{error_msg}\nStderr: {e.stderr}\nStdout: {e.stdout}")
        
        # Try to extract meaningful error from stderr
        if e.stderr:
            # Get last few lines which usually contain the actual error
            error_lines = e.stderr.strip().split('\n')
            relevant_error = '\n'.join(error_lines[-10:])
            raise RenderError(f"Rendering failed: {relevant_error}")
        else:
            raise RenderError(error_msg)
            
    except Exception as e:
        logger.error(f"Unexpected error during rendering: {str(e)}", exc_info=True)
        raise RenderError(f"Unexpected rendering error: {str(e)}")


def get_video_path() -> Path:
    """Get the expected path to the rendered video."""
    return settings.media_dir / "720p30" / settings.output_video_file


def get_video_url() -> str:
    """Get the URL path to access the video."""
    return f"/videos/generated_animation/720p30/{settings.output_video_file}"
