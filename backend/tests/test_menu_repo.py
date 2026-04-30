"""Unit tests for MenuRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.menu import Menu
from backend.app.repositories.menu_repo import MenuRepository


@pytest.fixture
def repo():
    """Create a MenuRepository instance."""
    return MenuRepository()


@pytest_asyncio.fixture
async def sample_category(db_session: AsyncSession) -> Category:
    """Create a sample category for testing."""
    category = Category(store_id=1, name="메인 메뉴", display_order=0)
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def second_category(db_session: AsyncSession) -> Category:
    """Create a second category for testing."""
    category = Category(store_id=1, name="사이드", display_order=1)
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
class TestMenuRepositoryCreate:
    """Tests for menu creation."""

    async def test_create_menu_success(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test creating a menu item."""
        menu = await repo.create(
            store_id=1,
            category_id=sample_category.id,
            name="김치찌개",
            price=9000,
            description="매콤한 김치찌개",
            image_path=None,
            db=db_session,
        )
        await db_session.commit()

        assert menu.id is not None
        assert menu.name == "김치찌개"
        assert menu.price == 9000
        assert menu.description == "매콤한 김치찌개"
        assert menu.display_order == 0
        assert menu.is_available is True

    async def test_create_multiple_menus_auto_order(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test auto-incrementing display_order."""
        m1 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        m2 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="된장찌개", price=8000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        assert m1.display_order == 0
        assert m2.display_order == 1


@pytest.mark.asyncio
class TestMenuRepositoryRead:
    """Tests for menu retrieval."""

    async def test_get_by_store(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test getting menus by store."""
        await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        await repo.create(
            store_id=1, category_id=sample_category.id,
            name="된장찌개", price=8000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        menus = await repo.get_by_store(store_id=1, db=db_session)
        assert len(menus) == 2

    async def test_get_by_store_with_category_filter(
        self,
        repo: MenuRepository,
        db_session: AsyncSession,
        sample_category: Category,
        second_category: Category,
    ):
        """Test filtering menus by category."""
        await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        await repo.create(
            store_id=1, category_id=second_category.id,
            name="감자튀김", price=5000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        menus = await repo.get_by_store(
            store_id=1, db=db_session, category_id=sample_category.id
        )
        assert len(menus) == 1
        assert menus[0].name == "김치찌개"

    async def test_get_available_by_store(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test getting only available menus."""
        m1 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        m2 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="된장찌개", price=8000, description=None, image_path=None, db=db_session,
        )
        m2.is_available = False
        await db_session.commit()

        available = await repo.get_available_by_store(store_id=1, db=db_session)
        assert len(available) == 1
        assert available[0].name == "김치찌개"

    async def test_get_by_id(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test getting a menu by ID."""
        created = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        found = await repo.get_by_id(menu_id=created.id, db=db_session)
        assert found is not None
        assert found.name == "김치찌개"

    async def test_get_by_id_not_found(self, repo: MenuRepository, db_session: AsyncSession):
        """Test getting a non-existent menu."""
        found = await repo.get_by_id(menu_id=999, db=db_session)
        assert found is None


@pytest.mark.asyncio
class TestMenuRepositoryUpdate:
    """Tests for menu update."""

    async def test_update_menu_fields(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test updating menu fields."""
        menu = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        updated = await repo.update(
            menu=menu, db=db_session, name="특제 김치찌개", price=12000
        )
        await db_session.commit()

        assert updated.name == "특제 김치찌개"
        assert updated.price == 12000


@pytest.mark.asyncio
class TestMenuRepositoryDelete:
    """Tests for menu deletion."""

    async def test_delete_menu_and_reorder(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test deleting a menu and reordering remaining menus."""
        m1 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        m2 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="된장찌개", price=8000, description=None, image_path=None, db=db_session,
        )
        m3 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="순두부", price=7000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        await repo.delete(menu=m2, db=db_session)
        await db_session.commit()

        remaining = await repo.get_by_store(
            store_id=1, db=db_session, category_id=sample_category.id
        )
        assert len(remaining) == 2
        assert remaining[0].display_order == 0
        assert remaining[1].display_order == 1


@pytest.mark.asyncio
class TestMenuRepositoryReorder:
    """Tests for menu reordering."""

    async def test_reorder_menu(
        self, repo: MenuRepository, db_session: AsyncSession, sample_category: Category
    ):
        """Test reordering a menu item."""
        m1 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="김치찌개", price=9000, description=None, image_path=None, db=db_session,
        )
        m2 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="된장찌개", price=8000, description=None, image_path=None, db=db_session,
        )
        m3 = await repo.create(
            store_id=1, category_id=sample_category.id,
            name="순두부", price=7000, description=None, image_path=None, db=db_session,
        )
        await db_session.commit()

        # Move m3 (order 2) to position 0
        await repo.reorder(menu=m3, new_order=0, db=db_session)
        await db_session.commit()

        menus = await repo.get_by_store(
            store_id=1, db=db_session, category_id=sample_category.id
        )
        names_in_order = [m.name for m in menus]
        assert names_in_order[0] == "순두부"
