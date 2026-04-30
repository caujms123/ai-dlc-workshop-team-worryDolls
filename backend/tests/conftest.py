"""테스트 공통 Fixture 정의 (Unit 2 + Unit 3)."""

import asyncio
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.order import Order, OrderItem, OrderHistory, OrderStatus, PaymentType


# 테스트용 SQLite 인메모리 엔진
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """세션 범위 이벤트 루프."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 DB 세션 (각 테스트마다 초기화)."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def sample_order(db_session: AsyncSession) -> Order:
    """테스트용 샘플 주문 생성."""
    order = Order(
        order_number="ORD-20260430-0001",
        store_id=1,
        table_id=1,
        session_id=1,
        status=OrderStatus.PENDING,
        payment_type=PaymentType.SINGLE_PAY,
        total_amount=25000,
        ordered_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(order)
    await db_session.flush()

    items = [
        OrderItem(
            order_id=order.id,
            menu_id=1,
            menu_name="김치찌개",
            quantity=2,
            unit_price=8000,
            subtotal=16000,
        ),
        OrderItem(
            order_id=order.id,
            menu_id=2,
            menu_name="된장찌개",
            quantity=1,
            unit_price=9000,
            subtotal=9000,
        ),
    ]
    db_session.add_all(items)
    await db_session.flush()
    await db_session.refresh(order, attribute_names=["items"])
    return order
