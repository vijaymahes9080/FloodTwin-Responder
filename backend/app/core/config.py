"""
Application Configuration for FLOODTWIN RESPONDER.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FloodTwin Responder"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Environment & Mock Mode
    ENVIRONMENT: str = "development"
    MOCK_NOTIFICATION_MODE: bool = True  # Invariant: Must default to True
    
    # Security & Auth
    SECRET_KEY: str = "floodtwin-super-secret-key-for-dev-use-only-do-not-commit-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./floodtwin.db"
    
    # Operational District: Chennai Flood Basin
    DISTRICT_NAME: str = "Chennai Metropolitan District"
    DEFAULT_LAT: float = 13.040
    DEFAULT_LON: float = 80.230

    class Config:
        case_sensitive = True
        extra = "ignore"


settings = Settings()
