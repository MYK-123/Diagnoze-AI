from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    api_title: str = "Diagnoze AI API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    # Database (for future use)
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
