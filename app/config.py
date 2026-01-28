from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import secrets
import os

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    For production, create a .env file based on .env.example
    and set all sensitive values there.
    """
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True
    )

    # Application
    APP_NAME: str = "Trexim v3"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Security Keys
    # In production, these MUST be set via environment variables
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

    # Admin - initial setup password (used only for first admin creation)
    # After first admin is created, this is ignored
    ADMIN_INIT_USERNAME: str = os.getenv("ADMIN_INIT_USERNAME", "admin")
    ADMIN_INIT_PASSWORD: str = os.getenv("ADMIN_INIT_PASSWORD", "")
    
    # Database
    DATABASE_URL: str = "sqlite:///./trexim.db"
    
    # File Uploads
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    @field_validator("SECRET_KEY", "SESSION_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v: str, info) -> str:
        """Warn if using default secret keys in production"""
        if v == "your-secret-key-here-change-in-production":
            print(f"⚠️  WARNING: Using default {info.field_name}! Set it in .env for production!")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV.lower() == "production"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
