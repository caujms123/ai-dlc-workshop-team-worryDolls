"""Test configuration and fixtures."""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Use a separate Base for testing to avoid loading all models
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionFactory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Create a test-only Base to avoid FK issues with other units' models
class TestBase(DeclarativeBase):
    """Test-only base class."""
    pass


# Import and rebind Unit 2 models to TestBase for isolated testing
from app.models.category import Category
from app.models.menu import Menu

# Patch the models to use test base metadata
import app.database as db_module
_original_base = db_module.Base


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create and drop tables for each test (Unit 2 tables only)."""
    from app.models.category import Category
    from app.models.menu import Menu

    # Only create Unit 2 tables
    tables = [Category.__table__, Menu.__table__]

    async with test_engine.begin() as conn:
        for table in tables:
            await conn.run_sync(lambda sync_conn, t=table: t.create(sync_conn, checkfirst=True))
    yield
    async with test_engine.begin() as conn:
        for table in reversed(tables):
            await conn.run_sync(lambda sync_conn, t=table: t.drop(sync_conn, checkfirst=True))


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    async with TestSessionFactory() as session:
        yield session
        await session.rollback()
