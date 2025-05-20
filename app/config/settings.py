from pydantic import Field, HttpUrl, PostgresDsn, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Optional, Dict, Any, Union
import secrets
import string

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "DocuGenie"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+") for _ in range(50))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days
    JWT_REFRESH_SECRET_KEY: str = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+") for _ in range(50))
    
    # Security Headers
    SECURE_HSTS_SECONDS: int = 31536000  # 1 year
    SECURE_SSL_REDIRECT: bool = False
    SESSION_COOKIE_SECURE: bool = True
    CSRF_COOKIE_SECURE: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    X_FRAME_OPTIONS: str = "DENY"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Database Settings
    DATABASE_URI: str = "sqlite:///./docugenie.db"
    TEST_DATABASE_URI: str = "sqlite:///./test_docugenie.db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URI
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "docugenie-documents"
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Document Processing Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FILE_TYPES: List[str] = [
        ".pdf", ".docx", ".doc", 
        ".jpg", ".jpeg", ".png", 
        ".tiff", ".tif", ".txt"
    ]
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@docugenie.com"
    EMAILS_FROM_NAME: str = "DocuGenie"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # First Superuser
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # Sentry Settings
    SENTRY_DSN: Optional[HttpUrl] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT: str = "100/minute"
    
    # Background Tasks
    MAX_WORKERS: int = 4
    
    # Testing
    TESTING: bool = False
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields in .env file
    )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        if self.ENVIRONMENT == "development":
            return ["*"]
        return self.BACKEND_CORS_ORIGINS

@lru_cache()
def get_settings():
    return Settings()
