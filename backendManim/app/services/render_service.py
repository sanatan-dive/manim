import subprocess
import logging
import sys
from pathlib import Path
import re
from datetime import datetime
from app.services.s3_service import s3_service
from config import settings

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Custom exception for rendering errors."""
    pass


def execute_manim() -> tuple[str, str]:
    """
    Execute manim to render the generated animation.
    
    Returns:
        tuple: (stdout, stderr) from the manim process
        
    Raises:
        RenderError: If rendering fails
    """
    try:
        script_path = settings.GENERATED_DIR / "animation.py"
        
        if not script_path.exists():
            raise RenderError("Animation script not found")
        
        logger.info("Starting Manim rendering...")
        
        # Run manim command using current python executable
        result = subprocess.run(
            [
                sys.executable, "-m", "manim",
                str(script_path),
                "GeneratedAnimation",
                "-ql",  # Low quality for faster preview (was -qm)
                "--media_dir", str(settings.MEDIA_DIR),
                "--format", "mp4"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        stdout = result.stdout
        stderr = result.stderr
        
        if result.returncode != 0:
            error_msg = f"Manim rendering failed with code {result.returncode}"
            logger.error(f"{error_msg}\nSTDERR: {stderr}")
            raise RenderError(error_msg)
        
        logger.info("Manim rendering completed successfully")
        return stdout, stderr
        
    except subprocess.TimeoutExpired:
        raise RenderError("Rendering timed out after 5 minutes")
    except Exception as e:
        logger.error(f"Rendering error: {str(e)}")
        raise RenderError(f"Rendering failed: {str(e)}")


def get_video_url() -> str:
    """
    Get the URL of the rendered video, uploading to S3 if configured.
    
    Returns:
        str: URL to access the video (local or S3)
        
    Raises:
        RenderError: If video file not found or upload fails
    """
    try:
        # Find the most recent video file
        # Default manim output structure: media/videos/{module_name}/{quality}/{scene_name}.mp4
        # We invoke manim on "generated/animation.py" so module name is "animation"
        # We use -ql so quality is "480p15"
        videos_dir = settings.VIDEOS_DIR / "animation" / "480p15"
        
        if not videos_dir.exists():
            raise RenderError("Video output directory not found")
        
        video_files = list(videos_dir.glob("*.mp4"))
        
        if not video_files:
            raise RenderError("No video file generated")
        
        # Get most recent file
        latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Found video file: {latest_video}")
        
        # Upload to S3 if enabled
        if settings.STORAGE_MODE == "s3":
            # Generate S3 key with timestamp
            timestamp = datetime.utcnow().strftime("%Y/%m/%d")
            s3_key = f"videos/{timestamp}/{latest_video.name}"
            
            logger.info(f"Uploading video to S3: {s3_key}")
            video_url = s3_service.upload_video(latest_video, s3_key)
            
            return video_url
        else:
            # Return local URL
            relative_path = latest_video.relative_to(settings.MEDIA_DIR)
            video_url = f"/videos/{relative_path}".replace("\\", "/")
            
            return video_url
        
    except Exception as e:
        logger.error(f"Error getting video URL: {str(e)}")
        raise RenderError(f"Failed to get video URL: {str(e)}")