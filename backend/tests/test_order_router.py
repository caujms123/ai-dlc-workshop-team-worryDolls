"""Order Router 단위 테스트."""

from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.middleware.auth import CurrentUser
from app.models.order import Order, OrderItem, OrderStatus, PaymentType, OrderHistory
from app.routers.order import router, get_order_service
from app.services.order_service import OrderService


# ── 테스트 앱 설정 ──

app = FastAPI()
app.include_router(router)


def _make_mock_order(
    order_id: int = 1,
    store_id: int = 1,
    table_id: int = 1,
    session_id: int = 1,
    status: str = "PENDING",
) -> MagicMock:
    """Mock Order 객체 생성."""
    order = MagicMock()
    order.id = order_id
    order.order_number = f"ORD-20260430-{order_id:04d}"
    order.store_id = store_id
    order.table_id = table_id
    order.session_id = session_id
    order.status = status
    order.payment_type = "SINGLE_PAY"
    order.total_amount = 25000
    order.ordered_at = datetime(2026, 4, 30, 12, 0, 0)
    order.updated_at = datetime(2026, 4, 30, 12, 0, 0)
    item = MagicMock()
    item.id = 1
    item.order_id = order_id
    item.menu_id = 1
    item.menu_name = "김치찌개"
    item.quantity = 2
    item.unit_price = 8000
    item.subtotal = 16000
    order.items = [item]
    return order


def _mock_store_admin(store_id: int = 1) -> CurrentUser:
    """Mock STORE_ADMIN 사용자."""
    return CurrentUser(user_id=1, role="STORE_ADMIN", store_id=store_id)


def _mock_table_user(store_id: int = 1, table_id: int = 1) -> CurrentUser:
    """Mock TABLE 사용자."""
    return CurrentUser(user_id=0, role="TABLE", store_id=store_id, table_id=table_id)


@pytest.fixture
def mock_order_service() -> AsyncMock:
    """Mock OrderService."""
    return AsyncMock(spec=OrderService)


@pytest_asyncio.fixture
async def admin_client(mock_order_service):
    """STORE_ADMIN 인증된 테스트 클라이언트."""
    from app.middleware.auth import get_current_user

    app.dependency_overrides[get_order_service] = lambda: mock_order_service
    app.dependency_overrides[get_current_user] = lambda: _mock_store_admin()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def table_client(mock_order_service):
    """TABLE 인증된 테스트 클라이언트."""
    from app.middleware.auth import get_current_user

    app.dependency_overrides[get_order_service] = lambda: mock_order_service
    app.dependency_overrides[get_current_user] = lambda: _mock_table_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


# ── POST /api/orders 테스트 ──


@pytest.mark.asyncio
async def test_create_order_success(table_client, mock_order_service):
    """주문 생성 성공 테스트."""
    mock_order_service.create_order.return_value = _make_mock_order()
    response = await table_client.post(
        "/api/orders",
        json={
            "table_id": 1,
            "payment_type": "SINGLE_PAY",
            "items": [{"menu_id": 1, "quantity": 2}],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["order_number"] == "ORD-20260430-0001"
    assert data["total_amount"] == 25000


@pytest.mark.asyncio
async def test_create_order_empty_items(table_client):
    """빈 주문 항목 검증 테스트."""
    response = await table_client.post(
        "/api/orders",
        json={"table_id": 1, "payment_type": "SINGLE_PAY", "items": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_invalid_payment_type(table_client):
    """잘못된 결제 방식 검증 테스트."""
    response = await table_client.post(
        "/api/orders",
        json={
            "table_id": 1,
            "payment_type": "INVALID",
            "items": [{"menu_id": 1, "quantity": 1}],
        },
    )
    assert response.status_code == 422


# ── GET /api/tables/{table_id}/orders 테스트 ──


@pytest.mark.asyncio
async def test_get_table_orders(table_client, mock_order_service):
    """테이블 주문 조회 테스트."""
    mock_order_service.get_table_orders.return_value = [_make_mock_order()]
    response = await table_client.get("/api/tables/1/orders?session_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# ── GET /api/stores/{store_id}/orders 테스트 ──


@pytest.mark.asyncio
async def test_get_store_orders(admin_client, mock_order_service):
    """매장 전체 주문 조회 테스트."""
    mock_order_service.get_store_orders.return_value = [_make_mock_order()]
    response = await admin_client.get("/api/stores/1/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_store_orders_wrong_store(admin_client, mock_order_service):
    """다른 매장 주문 조회 거부 테스트."""
    response = await admin_client.get("/api/stores/999/orders")
    assert response.status_code == 403


# ── PATCH /api/orders/{order_id}/status 테스트 ──


@pytest.mark.asyncio
async def test_update_order_status(admin_client, mock_order_service):
    """주문 상태 변경 테스트."""
    mock_order = _make_mock_order(status="PREPARING")
    mock_order_service.update_order_status.return_value = mock_order
    response = await admin_client.patch(
        "/api/orders/1/status", json={"status": "PREPARING"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"


@pytest.mark.asyncio
async def test_update_order_status_invalid(admin_client):
    """잘못된 상태값 검증 테스트."""
    response = await admin_client.patch(
        "/api/orders/1/status", json={"status": "INVALID"}
    )
    assert response.status_code == 422


# ── DELETE /api/orders/{order_id} 테스트 ──


@pytest.mark.asyncio
async def test_delete_order(admin_client, mock_order_service):
    """주문 삭제 테스트."""
    mock_order_service.delete_order.return_value = None
    response = await admin_client.delete("/api/orders/1")
    assert response.status_code == 204


# ── POST /api/tables/{table_id}/complete 테스트 ──


@pytest.mark.asyncio
async def test_complete_table(admin_client, mock_order_service):
    """이용 완료 처리 테스트."""
    mock_order_service.move_to_history.return_value = 3
    response = await admin_client.post("/api/tables/1/complete?session_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["moved_orders"] == 3


# ── GET /api/tables/{table_id}/order-history 테스트 ──


@pytest.mark.asyncio
async def test_get_order_history(admin_client, mock_order_service):
    """과거 주문 내역 조회 테스트."""
    mock_history = MagicMock()
    mock_history.id = 1
    mock_history.original_order_id = 1
    mock_history.order_number = "ORD-20260430-0001"
    mock_history.store_id = 1
    mock_history.table_id = 1
    mock_history.session_id = 1
    mock_history.status = "COMPLETED"
    mock_history.payment_type = "SINGLE_PAY"
    mock_history.total_amount = 25000
    mock_history.items_json = [{"menu_name": "김치찌개", "quantity": 2}]
    mock_history.ordered_at = datetime(2026, 4, 30, 12, 0, 0)
    mock_history.completed_at = datetime(2026, 4, 30, 14, 0, 0)
    mock_order_service.get_order_history.return_value = [mock_history]

    response = await admin_client.get("/api/tables/1/order-history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_number"] == "ORD-20260430-0001"


@pytest.mark.asyncio
async def test_get_order_history_with_date_filter(admin_client, mock_order_service):
    """날짜 필터 과거 주문 내역 조회 테스트."""
    mock_order_service.get_order_history.return_value = []
    response = await admin_client.get(
        "/api/tables/1/order-history?date_from=2026-04-01&date_to=2026-04-30"
    )
    assert response.status_code == 200
