"""Unit tests for CategoryRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.menu import Menu
from backend.app.repositories.category_repo import CategoryRepository


@pytest.fixture
def repo():
    """Create a CategoryRepository instance."""
    return CategoryRepository()


@pytest.mark.asyncio
class TestCategoryRepositoryCreate:
    """Tests for category creation."""

    async def test_create_category_success(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test creating a category with auto-assigned display_order."""
        category = await repo.create(store_id=1, name="메인 메뉴", db=db_session)
        await db_session.commit()

        assert category.id is not None
        assert category.store_id == 1
        assert category.name == "메인 메뉴"
        assert category.display_order == 0

    async def test_create_multiple_categories_auto_order(
        self, repo: CategoryRepository, db_session: AsyncSession
    ):
        """Test that display_order auto-increments for multiple categories."""
        cat1 = await repo.create(store_id=1, name="메인", db=db_session)
        cat2 = await repo.create(store_id=1, name="사이드", db=db_session)
        cat3 = await repo.create(store_id=1, name="음료", db=db_session)
        await db_session.commit()

        assert cat1.display_order == 0
        assert cat2.display_order == 1
        assert cat3.display_order == 2

    async def test_create_category_different_stores(
        self, repo: CategoryRepository, db_session: AsyncSession
    ):
        """Test that display_order is independent per store."""
        cat_store1 = await repo.create(store_id=1, name="메인", db=db_session)
        cat_store2 = await repo.create(store_id=2, name="메인", db=db_session)
        await db_session.commit()

        assert cat_store1.display_order == 0
        assert cat_store2.display_order == 0


@pytest.mark.asyncio
class TestCategoryRepositoryRead:
    """Tests for category retrieval."""

    async def test_get_by_store(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test getting categories by store ID."""
        await repo.create(store_id=1, name="메인", db=db_session)
        await repo.create(store_id=1, name="사이드", db=db_session)
        await repo.create(store_id=2, name="다른 매장", db=db_session)
        await db_session.commit()

        categories = await repo.get_by_store(store_id=1, db=db_session)
        assert len(categories) == 2
        assert categories[0].name == "메인"
        assert categories[1].name == "사이드"

    async def test_get_by_store_empty(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test getting categories for a store with no categories."""
        categories = await repo.get_by_store(store_id=999, db=db_session)
        assert len(categories) == 0

    async def test_get_by_id(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test getting a category by ID."""
        created = await repo.create(store_id=1, name="메인", db=db_session)
        await db_session.commit()

        found = await repo.get_by_id(category_id=created.id, db=db_session)
        assert found is not None
        assert found.name == "메인"

    async def test_get_by_id_not_found(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test getting a non-existent category."""
        found = await repo.get_by_id(category_id=999, db=db_session)
        assert found is None


@pytest.mark.asyncio
class TestCategoryRepositoryUpdate:
    """Tests for category update."""

    async def test_update_category_name(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test updating a category name."""
        category = await repo.create(store_id=1, name="메인", db=db_session)
        await db_session.commit()

        updated = await repo.update(category=category, name="메인 메뉴", db=db_session)
        await db_session.commit()

        assert updated.name == "메인 메뉴"


@pytest.mark.asyncio
class TestCategoryRepositoryDelete:
    """Tests for category deletion."""

    async def test_delete_category(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test deleting a category and reordering."""
        cat1 = await repo.create(store_id=1, name="메인", db=db_session)
        cat2 = await repo.create(store_id=1, name="사이드", db=db_session)
        cat3 = await repo.create(store_id=1, name="음료", db=db_session)
        await db_session.commit()

        await repo.delete(category=cat2, db=db_session)
        await db_session.commit()

        remaining = await repo.get_by_store(store_id=1, db=db_session)
        assert len(remaining) == 2
        assert remaining[0].display_order == 0
        assert remaining[1].display_order == 1

    async def test_count_menus_empty(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test counting menus in a category with no menus."""
        category = await repo.create(store_id=1, name="메인", db=db_session)
        await db_session.commit()

        count = await repo.count_menus(category_id=category.id, db=db_session)
        assert count == 0

    async def test_count_menus_with_menus(self, repo: CategoryRepository, db_session: AsyncSession):
        """Test counting menus in a category with menus."""
        category = await repo.create(store_id=1, name="메인", db=db_session)
        await db_session.commit()

        menu = Menu(
            store_id=1,
            category_id=category.id,
            name="김치찌개",
            price=9000,
            display_order=0,
        )
        db_session.add(menu)
        await db_session.commit()

        count = await repo.count_menus(category_id=category.id, db=db_session)
        assert count == 1
