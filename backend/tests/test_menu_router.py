"""Integration tests for Menu API router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.tests.conftest import test_engine, TestSessionFactory


@pytest_asyncio.fixture
async def client():
    """Create an async HTTP client for testing."""
    async def override_get_db():
        async with TestSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def category_id(client: AsyncClient) -> int:
    """Create a category and return its ID."""
    resp = await client.post(
        "/api/stores/1/categories",
        json={"name": "메인 메뉴"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
class TestMenuCreateAPI:
    """Tests for menu creation endpoint."""

    async def test_create_menu(self, client: AsyncClient, category_id: int):
        """Test POST /api/stores/{store_id}/menus."""
        response = await client.post(
            "/api/stores/1/menus",
            data={
                "name": "김치찌개",
                "price": "9000",
                "description": "매콤한 김치찌개",
                "category_id": str(category_id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "김치찌개"
        assert data["price"] == 9000
        assert data["store_id"] == 1

    async def test_create_menu_validation_error_price(
        self, client: AsyncClient, category_id: int
    ):
        """Test menu creation with invalid price (SECURITY-05)."""
        response = await client.post(
            "/api/stores/1/menus",
            data={
                "name": "김치찌개",
                "price": "-1",
                "category_id": str(category_id),
            },
        )
        assert response.status_code == 422

    async def test_create_menu_validation_error_name_too_short(
        self, client: AsyncClient, category_id: int
    ):
        """Test menu creation with name too short (SECURITY-05)."""
        response = await client.post(
            "/api/stores/1/menus",
            data={
                "name": "a",
                "price": "9000",
                "category_id": str(category_id),
            },
        )
        assert response.status_code == 422

    async def test_create_menu_invalid_category(self, client: AsyncClient):
        """Test menu creation with non-existent category."""
        response = await client.post(
            "/api/stores/1/menus",
            data={
                "name": "김치찌개",
                "price": "9000",
                "category_id": "999",
            },
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestMenuReadAPI:
    """Tests for menu retrieval endpoints."""

    async def test_get_menus(self, client: AsyncClient, category_id: int):
        """Test GET /api/stores/{store_id}/menus."""
        await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        await client.post(
            "/api/stores/1/menus",
            data={"name": "된장찌개", "price": "8000", "category_id": str(category_id)},
        )

        response = await client.get("/api/stores/1/menus")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_get_menus_with_category_filter(
        self, client: AsyncClient, category_id: int
    ):
        """Test GET with category_id filter."""
        await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )

        response = await client.get(
            f"/api/stores/1/menus?category_id={category_id}"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    async def test_get_menu_detail(self, client: AsyncClient, category_id: int):
        """Test GET /api/menus/{menu_id}."""
        create_resp = await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        menu_id = create_resp.json()["id"]

        response = await client.get(f"/api/menus/{menu_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "김치찌개"


@pytest.mark.asyncio
class TestMenuUpdateAPI:
    """Tests for menu update endpoint."""

    async def test_update_menu(self, client: AsyncClient, category_id: int):
        """Test PUT /api/menus/{menu_id}."""
        create_resp = await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        menu_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/menus/{menu_id}",
            data={"name": "특제 김치찌개", "price": "12000"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "특제 김치찌개"
        assert response.json()["price"] == 12000


@pytest.mark.asyncio
class TestMenuDeleteAPI:
    """Tests for menu deletion endpoint."""

    async def test_delete_menu(self, client: AsyncClient, category_id: int):
        """Test DELETE /api/menus/{menu_id}."""
        create_resp = await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        menu_id = create_resp.json()["id"]

        response = await client.delete(f"/api/menus/{menu_id}")
        assert response.status_code == 204

    async def test_delete_menu_not_found(self, client: AsyncClient):
        """Test DELETE with non-existent menu."""
        response = await client.delete("/api/menus/999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestMenuOrderAPI:
    """Tests for menu order endpoint."""

    async def test_update_menu_order(self, client: AsyncClient, category_id: int):
        """Test PUT /api/menus/{menu_id}/order."""
        create_resp = await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        menu_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/menus/{menu_id}/order",
            json={"display_order": 0},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestCustomerMenuAPI:
    """Tests for customer menu endpoint."""

    async def test_get_customer_menus(self, client: AsyncClient, category_id: int):
        """Test GET /api/customer/stores/{store_id}/menus."""
        await client.post(
            "/api/stores/1/menus",
            data={"name": "김치찌개", "price": "9000", "category_id": str(category_id)},
        )
        await client.post(
            "/api/stores/1/menus",
            data={"name": "된장찌개", "price": "8000", "category_id": str(category_id)},
        )

        response = await client.get("/api/customer/stores/1/menus")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1  # 1 category
        assert len(data["data"][0]["menus"]) == 2  # 2 menus

    async def test_get_customer_menus_empty(self, client: AsyncClient):
        """Test customer menus with no data."""
        response = await client.get("/api/customer/stores/999/menus")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 0
