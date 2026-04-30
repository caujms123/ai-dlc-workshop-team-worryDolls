"""데이터베이스 연결 및 세션 관리.

Unit 1에서 완성 예정. Unit 3에서는 Base와 세션 의존성만 정의.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI 의존성: 비동기 DB 세션 제공."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
