"""애플리케이션 설정.

Unit 1에서 완성 예정. Unit 3에서는 필요한 설정만 정의.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정."""

    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/table_order"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 16

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
