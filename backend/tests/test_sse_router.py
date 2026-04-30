"""SSE Router 단위 테스트."""

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.middleware.auth import CurrentUser, get_current_user
from app.routers.sse import router


app = FastAPI()
app.include_router(router)


def _mock_store_admin(store_id: int = 1) -> CurrentUser:
    return CurrentUser(user_id=1, role="STORE_ADMIN", store_id=store_id)


def _mock_table_user(table_id: int = 1) -> CurrentUser:
    return CurrentUser(user_id=0, role="TABLE", store_id=1, table_id=table_id)


# ── 관리자 SSE 엔드포인트 테스트 ──


@pytest.mark.asyncio
async def test_admin_sse_endpoint_returns_event_stream():
    """관리자 SSE 엔드포인트가 text/event-stream을 반환하는지 테스트."""
    app.dependency_overrides[get_current_user] = lambda: _mock_store_admin()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/sse/admin/stores/1/orders",
            headers={"Authorization": "Bearer test-token"},
            timeout=2.0,
        )
        # StreamingResponse이므로 200 + event-stream
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_sse_wrong_store():
    """다른 매장 SSE 접근 거부 테스트."""
    app.dependency_overrides[get_current_user] = lambda: _mock_store_admin(store_id=1)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/sse/admin/stores/999/orders",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 403

    app.dependency_overrides.clear()


# ── 고객 SSE 엔드포인트 테스트 ──


@pytest.mark.asyncio
async def test_customer_sse_endpoint_returns_event_stream():
    """고객 SSE 엔드포인트가 text/event-stream을 반환하는지 테스트."""
    app.dependency_overrides[get_current_user] = lambda: _mock_table_user(table_id=1)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/sse/customer/tables/1/orders",
            headers={"Authorization": "Bearer test-token"},
            timeout=2.0,
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_customer_sse_wrong_table():
    """다른 테이블 SSE 접근 거부 테스트."""
    app.dependency_overrides[get_current_user] = lambda: _mock_table_user(table_id=1)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/sse/customer/tables/999/orders",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 403

    app.dependency_overrides.clear()
