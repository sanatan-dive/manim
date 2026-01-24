import subprocess
import logging
import sys
import uuid
from pathlib import Path
import re
from datetime import datetime
from app.services.s3_service import s3_service
from config import settings

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Custom exception for rendering errors."""
    
    def __init__(self, message: str, stderr: str = "", code: str = ""):
        super().__init__(message)
        self.stderr = stderr
        self.code = code


def extract_error_details(stderr: str) -> str:
    """
    Extract the most relevant error information from Manim stderr output.
    
    Args:
        stderr: Full stderr output from Manim
        
    Returns:
        Cleaned error message with relevant context
    """
    if not stderr:
        return "Unknown error occurred during rendering"
    
    # 1. Remove ANSI escape sequences (colors, cursor movements, etc)
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKH]')
    clean_stderr = ansi_escape.sub('', stderr)
    
    # 2. Look for explicit Python exceptions (best quality)
    # We want the LAST one as that's usually the root cause in a traceback
    exception_pattern = r'(?:[a-zA-Z_][a-zA-Z0-9_.]*Error|Exception):\s+.+'
    exceptions = re.findall(exception_pattern, clean_stderr)
    
    if exceptions:
        return exceptions[-1].strip()

    # 3. Look for explicit Python exceptions at the VERY END of the output
    # This is often where Manim prints the final crash reason
    clean_lines = [line.strip() for line in clean_stderr.split('\n') if line.strip()]
    if clean_lines:
        # Check the last few lines for Error: patterns
        for line in reversed(clean_lines[-5:]): # Check last 5 lines
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*Error:', line):
                return line
            if "Exception:" in line:
                return line

    # 4. Fallback: Try to find error within the traceback context if possible
    # Rich traceback format: │ ❱  31 │   │   ).move_to(embedding_block.center)
    line_pattern = r'❱\s*(\d+)\s*│.*?│\s*(.+?)(?:\n|$)'
    line_match = re.search(line_pattern, clean_stderr)
    
    if line_match:
        line_num = line_match.group(1)
        code_line = line_match.group(2).strip()
        code_line = re.sub(r'[│╭╮╯╰─]', '', code_line).strip()
        return f"Error near line {line_num}: {code_line}"

    # 5. Last resort: Return the last non-empty line of the output
    if clean_lines:
        return f"Runtime Error: {clean_lines[-1]}"
    
    return "Unknown error occurred during rendering"


def get_generated_code() -> str:
    """Read the currently generated animation code."""
    try:
        script_path = settings.GENERATED_DIR / "animation.py"
        if script_path.exists():
            return script_path.read_text()
    except Exception as e:
        logger.warning(f"Could not read generated code: {e}")
    return ""


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
                "-qm",  # Medium quality (720p 30fps) for better compatibility
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
            # Include stderr and current code in the exception for retry logic
            current_code = get_generated_code()
            raise RenderError(error_msg, stderr=stderr, code=current_code)
        
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
        # We use -qm so quality is "720p30"
        videos_dir = settings.VIDEOS_DIR / "animation" / "720p30"
        
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
            # Generate S3 key with timestamp and UUID to prevent collisions & caching issues
            timestamp = datetime.utcnow().strftime("%Y/%m/%d")
            unique_id = str(uuid.uuid4())[:8]
            s3_key = f"videos/{timestamp}/{unique_id}_{latest_video.name}"
            
            logger.info(f"Uploading video to S3: {s3_key}")
            video_url = s3_service.upload_video(latest_video, s3_key)
            
            # Local file is deleted by s3_service.upload_video()

            return video_url
        else:
            # Return local URL
            relative_path = latest_video.relative_to(settings.MEDIA_DIR)
            video_url = f"/videos/{relative_path}".replace("\\", "/")
            
            return video_url
        
    except Exception as e:
        logger.error(f"Error getting video URL: {str(e)}")
        raise RenderError(f"Failed to get video URL: {str(e)}")