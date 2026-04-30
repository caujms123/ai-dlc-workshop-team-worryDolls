"""Unit tests for MenuService."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.menu import Menu
from app.schemas.category import CategoryCreate
from app.schemas.menu import MenuCreate, MenuOrderUpdate, MenuUpdate
from app.services.category_service import CategoryService
from app.services.menu_service import MenuService, SimpleFileUploadService


@pytest.fixture
def file_upload_service():
    """Create a mock file upload service."""
    mock = AsyncMock(spec=SimpleFileUploadService)
    mock.upload_image = AsyncMock(return_value="menus/1/test-uuid.jpg")
    mock.delete_image = AsyncMock()
    mock.validate_image = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def service(file_upload_service):
    """Create a MenuService instance with mocked file upload."""
    return MenuService(file_upload_service=file_upload_service)


@pytest.fixture
def category_service():
    """Create a CategoryService instance."""
    return CategoryService()


@pytest_asyncio.fixture
async def sample_category(
    category_service: CategoryService, db_session: AsyncSession
) -> Category:
    """Create a sample category."""
    cat = await category_service.create_category(
        store_id=1, data=CategoryCreate(name="메인 메뉴"), db=db_session
    )
    await db_session.commit()
    return cat


@pytest.mark.asyncio
class TestMenuServiceCreate:
    """Tests for menu creation."""

    async def test_create_menu_success(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test successful menu creation."""
        data = MenuCreate(
            name="김치찌개",
            price=9000,
            description="매콤한 김치찌개",
            category_id=sample_category.id,
        )
        menu = await service.create_menu(
            store_id=1, data=data, db=db_session
        )
        await db_session.commit()

        assert menu.id is not None
        assert menu.name == "김치찌개"
        assert menu.price == 9000
        assert menu.store_id == 1

    async def test_create_menu_with_image(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test menu creation with image upload."""
        data = MenuCreate(
            name="김치찌개",
            price=9000,
            category_id=sample_category.id,
        )
        mock_image = MagicMock(spec=UploadFile)
        mock_image.filename = "test.jpg"
        mock_image.content_type = "image/jpeg"

        menu = await service.create_menu(
            store_id=1, data=data, db=db_session, image=mock_image
        )
        await db_session.commit()

        assert menu.image_path == "menus/1/test-uuid.jpg"
        service.file_upload_service.upload_image.assert_called_once()

    async def test_create_menu_invalid_category(
        self,
        service: MenuService,
        db_session: AsyncSession,
    ):
        """Test menu creation with non-existent category."""
        data = MenuCreate(
            name="김치찌개",
            price=9000,
            category_id=999,
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create_menu(
                store_id=1, data=data, db=db_session
            )
        assert exc_info.value.status_code == 404

    async def test_create_menu_wrong_store_category(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test menu creation with category from different store (SECURITY-08)."""
        data = MenuCreate(
            name="김치찌개",
            price=9000,
            category_id=sample_category.id,  # belongs to store 1
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create_menu(
                store_id=2, data=data, db=db_session  # different store
            )
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
class TestMenuServiceRead:
    """Tests for menu retrieval."""

    async def test_get_menus(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test getting menus for a store."""
        await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        await service.create_menu(
            store_id=1,
            data=MenuCreate(name="된장찌개", price=8000, category_id=sample_category.id),
            db=db_session,
        )
        await db_session.commit()

        menus = await service.get_menus(store_id=1, db=db_session)
        assert len(menus) == 2

    async def test_get_menu_not_found(
        self, service: MenuService, db_session: AsyncSession
    ):
        """Test getting a non-existent menu."""
        with pytest.raises(HTTPException) as exc_info:
            await service.get_menu(menu_id=999, store_id=1, db=db_session)
        assert exc_info.value.status_code == 404

    async def test_get_menu_wrong_store(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test getting a menu from a different store (SECURITY-08)."""
        menu = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        await db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await service.get_menu(menu_id=menu.id, store_id=2, db=db_session)
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
class TestMenuServiceUpdate:
    """Tests for menu update."""

    async def test_update_menu_success(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test successful menu update."""
        menu = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        await db_session.commit()

        updated = await service.update_menu(
            menu_id=menu.id,
            store_id=1,
            data=MenuUpdate(name="특제 김치찌개", price=12000),
            db=db_session,
        )
        await db_session.commit()

        assert updated.name == "특제 김치찌개"
        assert updated.price == 12000

    async def test_update_menu_with_image_replacement(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
        file_upload_service,
    ):
        """Test menu update with image replacement (BR-MENU-03)."""
        # Create menu with image
        mock_image = MagicMock(spec=UploadFile)
        mock_image.filename = "old.jpg"
        mock_image.content_type = "image/jpeg"

        menu = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
            image=mock_image,
        )
        await db_session.commit()

        # Update with new image
        new_image = MagicMock(spec=UploadFile)
        new_image.filename = "new.jpg"
        new_image.content_type = "image/jpeg"
        file_upload_service.upload_image.return_value = "menus/1/new-uuid.jpg"

        updated = await service.update_menu(
            menu_id=menu.id,
            store_id=1,
            data=MenuUpdate(),
            db=db_session,
            image=new_image,
        )
        await db_session.commit()

        assert updated.image_path == "menus/1/new-uuid.jpg"
        file_upload_service.delete_image.assert_called_once_with("menus/1/test-uuid.jpg")


@pytest.mark.asyncio
class TestMenuServiceDelete:
    """Tests for menu deletion."""

    async def test_delete_menu_success(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test successful menu deletion."""
        menu = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        await db_session.commit()

        await service.delete_menu(
            menu_id=menu.id, store_id=1, db=db_session
        )
        await db_session.commit()

        menus = await service.get_menus(store_id=1, db=db_session)
        assert len(menus) == 0

    async def test_delete_menu_with_image(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
        file_upload_service,
    ):
        """Test menu deletion also deletes image file (BR-MENU-03)."""
        mock_image = MagicMock(spec=UploadFile)
        mock_image.filename = "test.jpg"
        mock_image.content_type = "image/jpeg"

        menu = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
            image=mock_image,
        )
        await db_session.commit()

        await service.delete_menu(
            menu_id=menu.id, store_id=1, db=db_session
        )
        await db_session.commit()

        file_upload_service.delete_image.assert_called_once_with("menus/1/test-uuid.jpg")


@pytest.mark.asyncio
class TestMenuServiceCustomerView:
    """Tests for customer menu view."""

    async def test_get_customer_menus(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test getting customer menus grouped by category (BR-MENU-05)."""
        await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        await service.create_menu(
            store_id=1,
            data=MenuCreate(name="된장찌개", price=8000, category_id=sample_category.id),
            db=db_session,
        )
        await db_session.commit()

        result = await service.get_customer_menus(store_id=1, db=db_session)
        assert len(result) == 1
        assert result[0].category.name == "메인 메뉴"
        assert len(result[0].menus) == 2

    async def test_get_customer_menus_excludes_unavailable(
        self,
        service: MenuService,
        db_session: AsyncSession,
        sample_category: Category,
    ):
        """Test that unavailable menus are excluded from customer view."""
        m1 = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="김치찌개", price=9000, category_id=sample_category.id),
            db=db_session,
        )
        m2 = await service.create_menu(
            store_id=1,
            data=MenuCreate(name="된장찌개", price=8000, category_id=sample_category.id),
            db=db_session,
        )
        # Make one unavailable
        await service.update_menu(
            menu_id=m2.id,
            store_id=1,
            data=MenuUpdate(is_available=False),
            db=db_session,
        )
        await db_session.commit()

        result = await service.get_customer_menus(store_id=1, db=db_session)
        assert len(result) == 1
        assert len(result[0].menus) == 1
        assert result[0].menus[0].name == "김치찌개"
