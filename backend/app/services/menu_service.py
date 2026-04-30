"""Menu service for business logic."""

import logging
import os

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.models.menu import Menu
from backend.app.repositories.category_repo import CategoryRepository
from backend.app.repositories.menu_repo import MenuRepository
from backend.app.schemas.menu import (
    CategoryWithMenusResponse,
    CustomerMenuItemResponse,
    MenuCreate,
    MenuOrderUpdate,
    MenuUpdate,
)
from backend.app.schemas.category import CategoryResponse

logger = logging.getLogger(__name__)


class FileUploadServiceInterface:
    """Interface for FileUploadService (provided by Unit 1).

    This is a placeholder interface. Unit 1 will provide the actual implementation.
    """

    async def upload_image(self, file: UploadFile, directory: str) -> str:
        """Upload an image file and return the stored path."""
        raise NotImplementedError

    async def delete_image(self, file_path: str) -> None:
        """Delete an image file."""
        raise NotImplementedError

    async def validate_image(self, file: UploadFile) -> bool:
        """Validate image file type and size."""
        raise NotImplementedError


class SimpleFileUploadService(FileUploadServiceInterface):
    """Simple file upload implementation for standalone operation.

    This will be replaced by Unit 1's FileUploadService in integration.
    """

    def __init__(self, upload_dir: str = "uploads") -> None:
        self.upload_dir = upload_dir

    async def upload_image(self, file: UploadFile, directory: str) -> str:
        """Upload an image file to the local filesystem.

        Args:
            file: The uploaded file.
            directory: Subdirectory for storage.

        Returns:
            The relative file path.

        Raises:
            HTTPException: If upload fails.
        """
        import uuid

        if not await self.validate_image(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 이미지 형식입니다. JPG, PNG만 허용됩니다.",
            )

        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{ext}"
        dir_path = os.path.join(self.upload_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, filename)

        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            return os.path.join(directory, filename)
        except Exception as e:
            logger.error("File upload failed", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="파일 업로드에 실패했습니다.",
            )

    async def delete_image(self, file_path: str) -> None:
        """Delete an image file from the filesystem.

        Args:
            file_path: Relative path to the file.
        """
        full_path = os.path.join(self.upload_dir, file_path)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info("Image deleted", extra={"path": file_path})
        except OSError as e:
            logger.error(
                "Failed to delete image",
                extra={"path": file_path, "error": str(e)},
            )

    async def validate_image(self, file: UploadFile) -> bool:
        """Validate image file type.

        Args:
            file: The uploaded file.

        Returns:
            True if valid, False otherwise.
        """
        allowed_types = {"image/jpeg", "image/png"}
        return file.content_type in allowed_types


class MenuService:
    """Service layer for menu business logic."""

    def __init__(
        self,
        file_upload_service: FileUploadServiceInterface | None = None,
    ) -> None:
        self.menu_repo = MenuRepository()
        self.category_repo = CategoryRepository()
        self.file_upload_service = file_upload_service or SimpleFileUploadService()

    async def create_menu(
        self,
        store_id: int,
        data: MenuCreate,
        db: AsyncSession,
        image: UploadFile | None = None,
    ) -> Menu:
        """Create a new menu item.

        BR-MENU-01: Required field validation (via Pydantic schema).
        BR-MENU-02: Price validation (via Pydantic schema).
        BR-MENU-03: Image upload via FileUploadService.

        Args:
            store_id: The store ID.
            data: Menu creation data.
            db: Database session.
            image: Optional image file.

        Returns:
            The created menu.

        Raises:
            HTTPException: If validation fails or category not found.
        """
        # Verify category exists and belongs to the store
        await self._verify_category_scope(data.category_id, store_id, db)

        # Upload image if provided (BR-MENU-03)
        image_path = None
        if image:
            image_path = await self.file_upload_service.upload_image(
                image, f"menus/{store_id}"
            )

        try:
            menu = await self.menu_repo.create(
                store_id=store_id,
                category_id=data.category_id,
                name=data.name,
                price=data.price,
                description=data.description,
                image_path=image_path,
                db=db,
            )
            logger.info(
                "Menu created successfully",
                extra={"menu_id": menu.id, "store_id": store_id},
            )
            return menu
        except Exception as e:
            # Clean up uploaded image on failure (SECURITY-15: resource cleanup)
            if image_path:
                await self.file_upload_service.delete_image(image_path)
            logger.error(
                "Failed to create menu",
                extra={"store_id": store_id, "error": str(e)},
            )
            raise

    async def get_menus(
        self,
        store_id: int,
        db: AsyncSession,
        category_id: int | None = None,
    ) -> list[Menu]:
        """Get menus for a store, optionally filtered by category.

        Args:
            store_id: The store ID.
            db: Database session.
            category_id: Optional category filter.

        Returns:
            List of menus.
        """
        return await self.menu_repo.get_by_store(
            store_id=store_id, db=db, category_id=category_id
        )

    async def get_menu(
        self, menu_id: int, store_id: int, db: AsyncSession
    ) -> Menu:
        """Get a single menu item with scope verification.

        Args:
            menu_id: The menu ID.
            store_id: The store ID for scope check.
            db: Database session.

        Returns:
            The menu.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        return await self._get_menu_with_scope_check(menu_id, store_id, db)

    async def update_menu(
        self,
        menu_id: int,
        store_id: int,
        data: MenuUpdate,
        db: AsyncSession,
        image: UploadFile | None = None,
    ) -> Menu:
        """Update a menu item.

        BR-MENU-03: Image replacement (delete old, upload new).

        Args:
            menu_id: The menu ID.
            store_id: The store ID for scope check.
            data: Menu update data.
            db: Database session.
            image: Optional new image file.

        Returns:
            The updated menu.

        Raises:
            HTTPException: If not found, scope mismatch, or validation fails.
        """
        menu = await self._get_menu_with_scope_check(menu_id, store_id, db)

        # Verify new category if changed
        if data.category_id is not None and data.category_id != menu.category_id:
            await self._verify_category_scope(data.category_id, store_id, db)

        # Handle image replacement (BR-MENU-03)
        new_image_path = menu.image_path
        if image:
            # Upload new image first
            new_image_path = await self.file_upload_service.upload_image(
                image, f"menus/{store_id}"
            )
            # Delete old image
            if menu.image_path:
                await self.file_upload_service.delete_image(menu.image_path)

        try:
            update_fields = {}
            if data.name is not None:
                update_fields["name"] = data.name
            if data.price is not None:
                update_fields["price"] = data.price
            if data.description is not None:
                update_fields["description"] = data.description
            if data.category_id is not None:
                update_fields["category_id"] = data.category_id
            if data.is_available is not None:
                update_fields["is_available"] = data.is_available
            if image:
                update_fields["image_path"] = new_image_path

            updated = await self.menu_repo.update(
                menu=menu, db=db, **update_fields
            )
            logger.info(
                "Menu updated successfully",
                extra={"menu_id": menu_id},
            )
            return updated
        except Exception as e:
            logger.error(
                "Failed to update menu",
                extra={"menu_id": menu_id, "error": str(e)},
            )
            raise

    async def delete_menu(
        self, menu_id: int, store_id: int, db: AsyncSession
    ) -> None:
        """Delete a menu item and its image.

        BR-MENU-03: Delete image file on menu deletion.
        BR-MENU-04: Reorder remaining menus.

        Args:
            menu_id: The menu ID.
            store_id: The store ID for scope check.
            db: Database session.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        menu = await self._get_menu_with_scope_check(menu_id, store_id, db)

        # Delete image file if exists (BR-MENU-03)
        if menu.image_path:
            await self.file_upload_service.delete_image(menu.image_path)

        try:
            await self.menu_repo.delete(menu=menu, db=db)
            logger.info(
                "Menu deleted successfully",
                extra={"menu_id": menu_id, "store_id": store_id},
            )
        except Exception as e:
            logger.error(
                "Failed to delete menu",
                extra={"menu_id": menu_id, "error": str(e)},
            )
            raise

    async def update_menu_order(
        self,
        menu_id: int,
        store_id: int,
        data: MenuOrderUpdate,
        db: AsyncSession,
    ) -> Menu:
        """Update a menu's display order.

        BR-MENU-04: Reorder sibling menus.

        Args:
            menu_id: The menu ID.
            store_id: The store ID for scope check.
            data: Order update data.
            db: Database session.

        Returns:
            The reordered menu.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        menu = await self._get_menu_with_scope_check(menu_id, store_id, db)

        try:
            updated = await self.menu_repo.reorder(
                menu=menu, new_order=data.display_order, db=db
            )
            logger.info(
                "Menu order updated",
                extra={"menu_id": menu_id, "new_order": data.display_order},
            )
            return updated
        except Exception as e:
            logger.error(
                "Failed to update menu order",
                extra={"menu_id": menu_id, "error": str(e)},
            )
            raise

    async def get_customer_menus(
        self, store_id: int, db: AsyncSession
    ) -> list[CategoryWithMenusResponse]:
        """Get menus grouped by category for customer view.

        BR-MENU-05: Only available menus, grouped by category, ordered by display_order.

        Args:
            store_id: The store ID.
            db: Database session.

        Returns:
            List of categories with their available menus.
        """
        categories = await self.category_repo.get_by_store(
            store_id=store_id, db=db
        )

        result = []
        for cat in categories:
            menus = await self.menu_repo.get_available_by_category(
                category_id=cat.id, db=db
            )
            if menus:  # Only include categories that have available menus
                result.append(
                    CategoryWithMenusResponse(
                        category=CategoryResponse.model_validate(cat),
                        menus=[
                            CustomerMenuItemResponse.model_validate(m)
                            for m in menus
                        ],
                    )
                )
        return result

    async def _get_menu_with_scope_check(
        self, menu_id: int, store_id: int, db: AsyncSession
    ) -> Menu:
        """Get a menu and verify it belongs to the given store.

        SECURITY-08: Object-level authorization (IDOR prevention).

        Args:
            menu_id: The menu ID.
            store_id: The expected store ID.
            db: Database session.

        Returns:
            The menu.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        menu = await self.menu_repo.get_by_id(menu_id=menu_id, db=db)
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="메뉴를 찾을 수 없습니다.",
            )
        if menu.store_id != store_id:
            logger.warning(
                "Store scope mismatch for menu access",
                extra={
                    "menu_id": menu_id,
                    "expected_store": store_id,
                    "actual_store": menu.store_id,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 메뉴에 대한 접근 권한이 없습니다.",
            )
        return menu

    async def _verify_category_scope(
        self, category_id: int, store_id: int, db: AsyncSession
    ) -> Category:
        """Verify a category exists and belongs to the store.

        Args:
            category_id: The category ID.
            store_id: The expected store ID.
            db: Database session.

        Returns:
            The category.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        category = await self.category_repo.get_by_id(
            category_id=category_id, db=db
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )
        if category.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 카테고리에 대한 접근 권한이 없습니다.",
            )
        return category
