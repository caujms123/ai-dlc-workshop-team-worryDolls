"""OrderRepository 단위 테스트."""

from datetime import datetime, date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderHistory, OrderStatus, PaymentType
from app.repositories.order_repo import OrderRepository


@pytest.fixture
def repo() -> OrderRepository:
    """OrderRepository 인스턴스."""
    return OrderRepository()


# ── Order CRUD 테스트 ──


@pytest.mark.asyncio
async def test_create_order(db_session: AsyncSession, repo: OrderRepository):
    """주문 생성 테스트."""
    order = Order(
        order_number="ORD-20260430-0001",
        store_id=1,
        table_id=1,
        session_id=1,
        status=OrderStatus.PENDING,
        payment_type=PaymentType.SINGLE_PAY,
        total_amount=10000,
        ordered_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    result = await repo.create(order, db_session)
    assert result.id is not None
    assert result.order_number == "ORD-20260430-0001"
    assert result.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_id(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """ID로 주문 조회 테스트."""
    result = await repo.get_by_id(sample_order.id, db_session)
    assert result is not None
    assert result.order_number == sample_order.order_number
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_get_by_id_not_found(
    db_session: AsyncSession, repo: OrderRepository
):
    """존재하지 않는 주문 조회 테스트."""
    result = await repo.get_by_id(99999, db_session)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_session(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """세션별 주문 조회 테스트."""
    results = await repo.get_by_session(sample_order.session_id, db_session)
    assert len(results) == 1
    assert results[0].id == sample_order.id


@pytest.mark.asyncio
async def test_get_by_store(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """매장별 주문 조회 테스트."""
    results = await repo.get_by_store(sample_order.store_id, db_session)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_by_table_and_session(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """테이블+세션별 주문 조회 테스트."""
    results = await repo.get_by_table_and_session(
        sample_order.table_id, sample_order.session_id, db_session
    )
    assert len(results) == 1


@pytest.mark.asyncio
async def test_update_status(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """주문 상태 업데이트 테스트."""
    result = await repo.update_status(
        sample_order.id, OrderStatus.PREPARING, db_session
    )
    assert result is not None
    assert result.status == OrderStatus.PREPARING


@pytest.mark.asyncio
async def test_update_status_not_found(
    db_session: AsyncSession, repo: OrderRepository
):
    """존재하지 않는 주문 상태 업데이트 테스트."""
    result = await repo.update_status(99999, OrderStatus.PREPARING, db_session)
    assert result is None


@pytest.mark.asyncio
async def test_delete_order(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """주문 삭제 테스트."""
    result = await repo.delete_order(sample_order.id, db_session)
    assert result is True
    # 삭제 확인
    order = await repo.get_by_id(sample_order.id, db_session)
    assert order is None


@pytest.mark.asyncio
async def test_delete_order_not_found(
    db_session: AsyncSession, repo: OrderRepository
):
    """존재하지 않는 주문 삭제 테스트."""
    result = await repo.delete_order(99999, db_session)
    assert result is False


# ── count_today_orders 테스트 ──


@pytest.mark.asyncio
async def test_count_today_orders(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """오늘 주문 수 조회 테스트."""
    count = await repo.count_today_orders(
        sample_order.store_id, "20260430", db_session
    )
    assert count == 1


@pytest.mark.asyncio
async def test_count_today_orders_empty(
    db_session: AsyncSession, repo: OrderRepository
):
    """주문 없는 날 조회 테스트."""
    count = await repo.count_today_orders(1, "20260501", db_session)
    assert count == 0


# ── OrderItem 테스트 ──


@pytest.mark.asyncio
async def test_get_order_items(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """주문 항목 조회 테스트."""
    items = await repo.get_order_items(sample_order.id, db_session)
    assert len(items) == 2
    assert items[0].menu_name in ("김치찌개", "된장찌개")


@pytest.mark.asyncio
async def test_create_order_items(
    db_session: AsyncSession, repo: OrderRepository
):
    """주문 항목 일괄 생성 테스트."""
    order = Order(
        order_number="ORD-20260430-0099",
        store_id=1,
        table_id=1,
        session_id=1,
        status=OrderStatus.PENDING,
        payment_type=PaymentType.DUTCH_PAY,
        total_amount=5000,
        ordered_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(order)
    await db_session.flush()

    items = [
        OrderItem(
            order_id=order.id,
            menu_id=3,
            menu_name="비빔밥",
            quantity=1,
            unit_price=5000,
            subtotal=5000,
        )
    ]
    result = await repo.create_order_items(items, db_session)
    assert len(result) == 1


# ── OrderHistory 테스트 ──


@pytest.mark.asyncio
async def test_create_history(db_session: AsyncSession, repo: OrderRepository):
    """주문 이력 생성 테스트."""
    history = OrderHistory(
        original_order_id=1,
        order_number="ORD-20260430-0001",
        store_id=1,
        table_id=1,
        session_id=1,
        status="COMPLETED",
        payment_type="SINGLE_PAY",
        total_amount=25000,
        items_json=[{"menu_name": "김치찌개", "quantity": 2, "subtotal": 16000}],
        ordered_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    result = await repo.create_history(history, db_session)
    assert result.id is not None
    assert result.original_order_id == 1


@pytest.mark.asyncio
async def test_get_history_by_table(
    db_session: AsyncSession, repo: OrderRepository
):
    """테이블별 이력 조회 테스트."""
    history = OrderHistory(
        original_order_id=1,
        order_number="ORD-20260430-0001",
        store_id=1,
        table_id=1,
        session_id=1,
        status="COMPLETED",
        payment_type="SINGLE_PAY",
        total_amount=25000,
        items_json=[],
        ordered_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(history)
    await db_session.flush()

    results = await repo.get_history_by_table(1, db_session)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_table_total(
    db_session: AsyncSession, repo: OrderRepository, sample_order: Order
):
    """테이블 총 주문액 계산 테스트."""
    total = await repo.get_table_total(
        sample_order.table_id, sample_order.session_id, db_session
    )
    assert total == 25000
