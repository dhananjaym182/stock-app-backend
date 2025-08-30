from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:jay@localhost/indian_stocks_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Indian Stock Market API"
    VERSION: str = "2.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    OPENROUTER_API_KEY: str = "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"
    
    # Cache Settings
    CACHE_TTL_REALTIME: int = 30  # seconds
    CACHE_TTL_HISTORICAL: int = 86400  # 24 hours
    CACHE_TTL_COMPANY_INFO: int = 604800  # 7 days
    CACHE_TTL_FINANCIALS: int = 2592000  # 30 days
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
