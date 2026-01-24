from pydantic_settings import BaseSettings
from pathlib import Path
import os

def _load_system_instruction() -> str:
    try:
        return Path("prompt.md").read_text()
    except Exception:
        # Minimal fallback to avoid crashes if file is missing
        return "You are an expert Manim animation developer. Generate Python code using Manim."

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # API Configuration
    GEMINI_API_KEY: str
    SECRET_KEY: str | None = None
    MODEL_NAME: str = "gemini-2.5-pro"
    
    # AI Configuration
    dangerous_patterns: list[str] = ["import os", "import sys", "subprocess", "eval(", "exec(", "open("]
    
    system_instruction: str = _load_system_instruction()
    
    # Job Configuration
    MAX_JOB_HISTORY: int = 100
    JOB_TIMEOUT: int = 300  # 5 minutes hard limit
    JOB_SOFT_TIMEOUT: int = 240  # 4 minutes soft limit
    MAX_CONCURRENT_JOBS: int = 2  # Max jobs per user

    # Auth Configuration
    CLERK_ISSUER: str | None = None # e.g. https://clerk.your-domain.com
    CLERK_AUDIENCE: str | None = None
    
    # Database Configuration
    DATABASE_URL: str = "file:./dev.db"
    
    # Paths
    GENERATED_DIR: Path = Path("generated")
    MEDIA_DIR: Path = Path("media")
    VIDEOS_DIR: Path = Path("media/videos")
    generated_animation_file: Path = Path("generated/animation.py")
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str | None = None
    AWS_CLOUDFRONT_DOMAIN: str | None = None
    
    # Storage mode: 'local' or 's3'
    STORAGE_MODE: str = "local"
    
    @property
    def allowed_origins(self) -> list[str]:
        """Parse allowed origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def validate_api_key(self) -> bool:
        """Validate that API key is set."""
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY != "your-api-key-here")
    
    def validate_s3_config(self) -> bool:
        """Validate S3 configuration."""
        if self.STORAGE_MODE == "s3":
            return all([
                self.AWS_ACCESS_KEY_ID,
                self.AWS_SECRET_ACCESS_KEY,
                self.AWS_S3_BUCKET
            ])
        return True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

# Create necessary directories
settings.GENERATED_DIR.mkdir(exist_ok=True)
settings.MEDIA_DIR.mkdir(exist_ok=True)
settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)