from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SpinalSurgery Research Platform"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "spinalsurgery_research")
    DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    CLAUDE_SESSION_KEY: Optional[str] = os.getenv("CLAUDE_SESSION_KEY")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Email
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = os.getenv("SMTP_PORT", 587)
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()