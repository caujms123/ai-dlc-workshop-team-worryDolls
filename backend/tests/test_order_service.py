"""OrderService 단위 테스트."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderHistory, OrderStatus, PaymentType
from app.repositories.order_repo import OrderRepository
from app.schemas.order import OrderCreate, OrderItemCreate
from app.services.order_service import OrderService


# ── Mock 설정 ──


class MockMenu:
    """테스트용 Mock 메뉴."""

    def __init__(self, menu_id: int, name: str, price: int, store_id: int):
        self.id = menu_id
        self.name = name
        self.price = price
        self.store_id = store_id


class MockSession:
    """테스트용 Mock 세션."""

    def __init__(self, session_id: int = 1):
        self.id = session_id


@pytest.fixture
def mock_menu_service():
    """Mock MenuService."""
    service = AsyncMock()
    service.get_menu = AsyncMock(
        return_value=MockMenu(1, "김치찌개", 8000, 1)
    )
    return service


@pytest.fixture
def mock_table_service():
    """Mock TableService."""
    service = AsyncMock()
    service.get_or_create_session = AsyncMock(
        return_value=MockSession(1)
    )
    return service


@pytest_asyncio.fixture
async def order_service(
    mock_menu_service, mock_table_service
) -> OrderService:
    """OrderService 인스턴스 (Mock 의존성 주입)."""
    return OrderService(
        order_repo=OrderRepository(),
        menu_service=mock_menu_service,
        table_service=mock_table_service,
    )


# ── 주문 생성 테스트 ──


@pytest.mark.asyncio
async def test_create_order_success(
    db_session: AsyncSession, order_service: OrderService
):
    """주문 생성 성공 테스트."""
    order_data = OrderCreate(
        table_id=1,
        payment_type="SINGLE_PAY",
        items=[OrderItemCreate(menu_id=1, quantity=2)],
    )
    with patch("app.services.order_service.sse_manager") as mock_sse:
        mock_sse.publish_to_store = AsyncMock()
        result = await order_service.create_order(order_data, store_id=1, db=db_session)

    assert result.id is not None
    assert result.order_number.startswith("ORD-")
    assert result.status == OrderStatus.PENDING
    assert result.payment_type == PaymentType.SINGLE_PAY
    assert result.total_amount == 16000  # 8000 * 2


@pytest.mark.asyncio
async def test_create_order_menu_not_found(
    db_session: AsyncSession, order_service: OrderService
):
    """존재하지 않는 메뉴로 주문 생성 실패 테스트."""
    order_service.menu_service.get_menu = AsyncMock(return_value=None)
    order_data = OrderCreate(
        table_id=1,
        payment_type="DUTCH_PAY",
        items=[OrderItemCreate(menu_id=999, quantity=1)],
    )
    with pytest.raises(Exception) as exc_info:
        await order_service.create_order(order_data, store_id=1, db=db_session)
    assert "메뉴를 찾을 수 없습니다" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_order_wrong_store_menu(
    db_session: AsyncSession, order_service: OrderService
):
    """다른 매장의 메뉴로 주문 생성 실패 테스트."""
    order_service.menu_service.get_menu = AsyncMock(
        return_value=MockMenu(1, "김치찌개", 8000, store_id=999)
    )
    order_data = OrderCreate(
        table_id=1,
        payment_type="SINGLE_PAY",
        items=[OrderItemCreate(menu_id=1, quantity=1)],
    )
    with pytest.raises(Exception) as exc_info:
        await order_service.create_order(order_data, store_id=1, db=db_session)
    assert "해당 매장의 메뉴가 아닙니다" in str(exc_info.value.detail)


# ── 주문 번호 생성 테스트 ──


@pytest.mark.asyncio
async def test_generate_order_number(
    db_session: AsyncSession, order_service: OrderService
):
    """주문 번호 생성 형식 테스트."""
    number = await order_service._generate_order_number(store_id=1, db=db_session)
    assert number.startswith("ORD-")
    parts = number.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 4  # 0001


# ── 상태 전이 테스트 ──


@pytest.mark.asyncio
async def test_update_status_pending_to_preparing(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """PENDING → PREPARING 상태 전이 테스트."""
    with patch("app.services.order_service.sse_manager") as mock_sse:
        mock_sse.publish_to_store = AsyncMock()
        mock_sse.publish_to_table = AsyncMock()
        result = await order_service.update_order_status(
            sample_order.id, "PREPARING", sample_order.store_id, db_session
        )
    assert result.status == OrderStatus.PREPARING


@pytest.mark.asyncio
async def test_update_status_preparing_to_completed(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """PREPARING → COMPLETED 상태 전이 테스트."""
    # 먼저 PREPARING으로 변경
    with patch("app.services.order_service.sse_manager") as mock_sse:
        mock_sse.publish_to_store = AsyncMock()
        mock_sse.publish_to_table = AsyncMock()
        await order_service.update_order_status(
            sample_order.id, "PREPARING", sample_order.store_id, db_session
        )
        result = await order_service.update_order_status(
            sample_order.id, "COMPLETED", sample_order.store_id, db_session
        )
    assert result.status == OrderStatus.COMPLETED


@pytest.mark.asyncio
async def test_update_status_invalid_transition(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """잘못된 상태 전이 테스트 (PENDING → COMPLETED)."""
    with patch("app.services.order_service.sse_manager"):
        with pytest.raises(Exception) as exc_info:
            await order_service.update_order_status(
                sample_order.id, "COMPLETED", sample_order.store_id, db_session
            )
    assert "잘못된 상태 전이" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_status_order_not_found(
    db_session: AsyncSession, order_service: OrderService
):
    """존재하지 않는 주문 상태 변경 테스트."""
    with pytest.raises(Exception) as exc_info:
        await order_service.update_order_status(99999, "PREPARING", 1, db_session)
    assert "주문을 찾을 수 없습니다" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_status_wrong_store(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """다른 매장의 주문 상태 변경 시도 테스트."""
    with pytest.raises(Exception) as exc_info:
        await order_service.update_order_status(
            sample_order.id, "PREPARING", store_id=999, db=db_session
        )
    assert "해당 매장의 주문이 아닙니다" in str(exc_info.value.detail)


# ── 주문 삭제 테스트 ──


@pytest.mark.asyncio
async def test_delete_order_success(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """주문 삭제 성공 테스트."""
    with patch("app.services.order_service.sse_manager") as mock_sse:
        mock_sse.publish_to_store = AsyncMock()
        await order_service.delete_order(
            sample_order.id, sample_order.store_id, db_session
        )
    # 삭제 확인
    result = await order_service.order_repo.get_by_id(sample_order.id, db_session)
    assert result is None


@pytest.mark.asyncio
async def test_delete_order_not_found(
    db_session: AsyncSession, order_service: OrderService
):
    """존재하지 않는 주문 삭제 테스트."""
    with pytest.raises(Exception) as exc_info:
        await order_service.delete_order(99999, 1, db_session)
    assert "주문을 찾을 수 없습니다" in str(exc_info.value.detail)


# ── 이력 이동 테스트 ──


@pytest.mark.asyncio
async def test_move_to_history(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """이력 이동 테스트."""
    with patch("app.services.order_service.sse_manager") as mock_sse:
        mock_sse.publish_to_store = AsyncMock()
        moved = await order_service.move_to_history(
            sample_order.session_id, sample_order.store_id, db_session
        )
    assert moved == 1
    # 원본 삭제 확인
    orders = await order_service.order_repo.get_by_session(
        sample_order.session_id, db_session
    )
    assert len(orders) == 0
    # 이력 생성 확인
    history = await order_service.order_repo.get_history_by_table(
        sample_order.table_id, db_session
    )
    assert len(history) == 1
    assert history[0].original_order_id == sample_order.id


@pytest.mark.asyncio
async def test_move_to_history_empty_session(
    db_session: AsyncSession, order_service: OrderService
):
    """빈 세션 이력 이동 테스트."""
    with patch("app.services.order_service.sse_manager"):
        moved = await order_service.move_to_history(99999, 1, db_session)
    assert moved == 0


# ── 매장 전체 주문 조회 테스트 ──


@pytest.mark.asyncio
async def test_get_store_orders(
    db_session: AsyncSession, order_service: OrderService, sample_order: Order
):
    """매장 전체 주문 조회 테스트."""
    results = await order_service.get_store_orders(
        sample_order.store_id, db_session
    )
    assert len(results) == 1
    assert results[0].id == sample_order.id
