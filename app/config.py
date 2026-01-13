from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"
    )

    APP_NAME: str = "Trexim v3"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ADMIN_PASSWORD: str = "trexim2026"
    DATABASE_URL: str = "sqlite:///./trexim.db"
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 5242880
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

settings = Settings()
