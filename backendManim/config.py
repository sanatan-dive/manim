from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Configuration settings for Manim animation generation with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Required API Configuration
    GEMINI_API_KEY: str
    
    # AI Model Configuration
    MODEL_NAME: str = "gemini-2.5-pro"
    
    # File Configuration
    generated_dir: Path = Path("generated")
    generated_animation_file: Path = Path("generated/animation.py")
    output_video_file: str = "output_animation.mp4"
    media_dir: Path = Path("media/videos/generated_animation")
    
    # Manim Configuration
    manim_quality: str = "-qm"
    animation_class_name: str = "GeneratedAnimation"
    manim_timeout: int = 300  # 5 minutes
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Job Storage (in-memory for Phase 2)
    max_job_history: int = 100
    
        # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # System Instruction
    system_instruction: str = (
        "You are a Manim expert. Write a complete Python script using Manim Community Edition. "
        "Return ONLY the raw Python code. Do not use Markdown backticks. "
        "The class name must be 'GeneratedAnimation'. "
        "Do not use .to_center(), use .center() instead. "
        "IMPORTANT: Do not use MathTex or Tex classes, as the system lacks LaTeX. "
        "Use the Text class for all text labels. Do not use LaTeX syntax (like \\pi). "
        "Do not import or use dangerous modules like os, subprocess, sys, or eval."
    )
    
    # Security: Dangerous patterns to check in generated code
    dangerous_patterns: list[str] = [
        "import os",
        "import sys", 
        "import subprocess",
        "eval(",
        "exec(",
        "compile(",
        "__import__",
        "open(",
        "file(",
        "input(",
        "raw_input(",
        "execfile(",
    ]
    
    def validate_api_key(self) -> bool:
        """Validate that API key is set and not empty."""
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)


# Create global settings instance
settings = Settings()

# Validate configuration on startup
if not settings.validate_api_key():
    raise ValueError(
        "GEMINI_API_KEY is not set or is empty. "
        "Please set it in your .env file or environment variables."
    )

# Ensure required directories exist
settings.ensure_directories()


__all__ = ['settings', 'Settings']