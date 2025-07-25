from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SpinalSurgery Research Platform"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # SQLite Database (로컬 개발용)
    DATABASE_URL: str = "sqlite+aiosqlite:///./spinalsurgery_research.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
    ]
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()