"""데이터베이스 연결 설정"""

import os
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:password@localhost:3306/table_order"
)


class Base(DeclarativeBase):
    pass


# Lazy initialization - 실제 DB 연결은 필요할 때만 생성
_engine = None
_async_session_maker = None


def _get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        _engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    return _engine


def _get_session_maker():
    global _async_session_maker
    if _async_session_maker is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _async_session_maker = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_maker


async def get_db():
    """Dependency Injection용 DB 세션 제공"""
    session_maker = _get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
