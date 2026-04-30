"""Integration tests for Category API router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base
from app.main import app
from tests.conftest import test_engine, TestSessionFactory
from app.database import get_db
from app.models.category import Category
from app.models.menu import Menu


@pytest_asyncio.fixture
async def client():
    """Create an async HTTP client for testing."""
    # Override database dependency
    async def override_get_db():
        async with TestSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    tables = [Category.__table__, Menu.__table__]
    async with test_engine.begin() as conn:
        for table in tables:
            await conn.run_sync(lambda sync_conn, t=table: t.create(sync_conn, checkfirst=True))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    async with test_engine.begin() as conn:
        for table in reversed(tables):
            await conn.run_sync(lambda sync_conn, t=table: t.drop(sync_conn, checkfirst=True))

    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestCategoryAPI:
    """Tests for Category API endpoints."""

    async def test_create_category(self, client: AsyncClient):
        """Test POST /api/stores/{store_id}/categories."""
        response = await client.post(
            "/api/stores/1/categories",
            json={"name": "메인 메뉴"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "메인 메뉴"
        assert data["store_id"] == 1
        assert data["display_order"] == 0

    async def test_create_category_validation_error(self, client: AsyncClient):
        """Test POST with invalid data (SECURITY-05)."""
        response = await client.post(
            "/api/stores/1/categories",
            json={"name": "a"},  # Too short (min 2)
        )
        assert response.status_code == 422

    async def test_get_categories(self, client: AsyncClient):
        """Test GET /api/stores/{store_id}/categories."""
        # Create categories
        await client.post("/api/stores/1/categories", json={"name": "메인"})
        await client.post("/api/stores/1/categories", json={"name": "사이드"})

        response = await client.get("/api/stores/1/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["categories"]) == 2

    async def test_get_categories_empty(self, client: AsyncClient):
        """Test GET with no categories."""
        response = await client.get("/api/stores/999/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    async def test_update_category(self, client: AsyncClient):
        """Test PUT /api/categories/{category_id}."""
        create_resp = await client.post(
            "/api/stores/1/categories", json={"name": "메인"}
        )
        category_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/categories/{category_id}",
            json={"name": "메인 메뉴"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "메인 메뉴"

    async def test_update_category_not_found(self, client: AsyncClient):
        """Test PUT with non-existent category."""
        response = await client.put(
            "/api/categories/999",
            json={"name": "테스트"},
        )
        assert response.status_code == 404

    async def test_delete_category(self, client: AsyncClient):
        """Test DELETE /api/categories/{category_id}."""
        create_resp = await client.post(
            "/api/stores/1/categories", json={"name": "삭제할 카테고리"}
        )
        category_id = create_resp.json()["id"]

        response = await client.delete(f"/api/categories/{category_id}")
        assert response.status_code == 204

    async def test_delete_category_with_menus_fails(self, client: AsyncClient):
        """Test DELETE category with menus returns 409 (BR-CAT-02)."""
        # Create category
        cat_resp = await client.post(
            "/api/stores/1/categories", json={"name": "메인"}
        )
        category_id = cat_resp.json()["id"]

        # Create menu in that category
        await client.post(
            "/api/stores/1/menus",
            data={
                "name": "김치찌개",
                "price": "9000",
                "category_id": str(category_id),
            },
        )

        # Try to delete category
        response = await client.delete(f"/api/categories/{category_id}")
        assert response.status_code == 409
        assert "메뉴가 존재합니다" in response.json()["detail"]
