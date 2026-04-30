"""애플리케이션 설정 모듈."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """환경 변수 기반 애플리케이션 설정."""

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/table_order"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-256-bit-random-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 16

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    LOGIN_RATE_LIMIT: str = "5/15minutes"
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
