"""Unit tests for CategoryService."""

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.menu import Menu
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import CategoryService


@pytest.fixture
def service():
    """Create a CategoryService instance."""
    return CategoryService()


@pytest.mark.asyncio
class TestCategoryServiceCreate:
    """Tests for category creation."""

    async def test_create_category_success(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test successful category creation."""
        data = CategoryCreate(name="메인 메뉴")
        category = await service.create_category(
            store_id=1, data=data, db=db_session
        )
        await db_session.commit()

        assert category.id is not None
        assert category.name == "메인 메뉴"
        assert category.store_id == 1
        assert category.display_order == 0


@pytest.mark.asyncio
class TestCategoryServiceRead:
    """Tests for category retrieval."""

    async def test_get_categories(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test getting all categories for a store."""
        await service.create_category(
            store_id=1, data=CategoryCreate(name="메인"), db=db_session
        )
        await service.create_category(
            store_id=1, data=CategoryCreate(name="사이드"), db=db_session
        )
        await db_session.commit()

        categories = await service.get_categories(store_id=1, db=db_session)
        assert len(categories) == 2


@pytest.mark.asyncio
class TestCategoryServiceUpdate:
    """Tests for category update."""

    async def test_update_category_success(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test successful category update."""
        category = await service.create_category(
            store_id=1, data=CategoryCreate(name="메인"), db=db_session
        )
        await db_session.commit()

        updated = await service.update_category(
            category_id=category.id,
            store_id=1,
            data=CategoryUpdate(name="메인 메뉴"),
            db=db_session,
        )
        await db_session.commit()

        assert updated.name == "메인 메뉴"

    async def test_update_category_not_found(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test updating a non-existent category."""
        with pytest.raises(HTTPException) as exc_info:
            await service.update_category(
                category_id=999,
                store_id=1,
                data=CategoryUpdate(name="테스트"),
                db=db_session,
            )
        assert exc_info.value.status_code == 404

    async def test_update_category_wrong_store(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test updating a category from a different store (SECURITY-08)."""
        category = await service.create_category(
            store_id=1, data=CategoryCreate(name="메인"), db=db_session
        )
        await db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await service.update_category(
                category_id=category.id,
                store_id=2,  # Different store
                data=CategoryUpdate(name="해킹"),
                db=db_session,
            )
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
class TestCategoryServiceDelete:
    """Tests for category deletion."""

    async def test_delete_category_success(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test successful category deletion."""
        category = await service.create_category(
            store_id=1, data=CategoryCreate(name="삭제할 카테고리"), db=db_session
        )
        await db_session.commit()

        await service.delete_category(
            category_id=category.id, store_id=1, db=db_session
        )
        await db_session.commit()

        categories = await service.get_categories(store_id=1, db=db_session)
        assert len(categories) == 0

    async def test_delete_category_with_menus_fails(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test that deleting a category with menus fails (BR-CAT-02)."""
        category = await service.create_category(
            store_id=1, data=CategoryCreate(name="메인"), db=db_session
        )
        await db_session.commit()

        # Add a menu to the category
        menu = Menu(
            store_id=1,
            category_id=category.id,
            name="김치찌개",
            price=9000,
            display_order=0,
        )
        db_session.add(menu)
        await db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_category(
                category_id=category.id, store_id=1, db=db_session
            )
        assert exc_info.value.status_code == 409
        assert "메뉴가 존재합니다" in exc_info.value.detail

    async def test_delete_category_not_found(
        self, service: CategoryService, db_session: AsyncSession
    ):
        """Test deleting a non-existent category."""
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_category(
                category_id=999, store_id=1, db=db_session
            )
        assert exc_info.value.status_code == 404
