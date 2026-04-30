"""Category service for business logic."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category
from backend.app.repositories.category_repo import CategoryRepository
from backend.app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    """Service layer for category business logic."""

    def __init__(self) -> None:
        self.repo = CategoryRepository()

    async def create_category(
        self, store_id: int, data: CategoryCreate, db: AsyncSession
    ) -> Category:
        """Create a new category for a store.

        BR-CAT-01: display_order is auto-assigned (last + 1).

        Args:
            store_id: The store ID.
            data: Category creation data.
            db: Database session.

        Returns:
            The created category.

        Raises:
            HTTPException: If validation fails.
        """
        try:
            category = await self.repo.create(
                store_id=store_id, name=data.name, db=db
            )
            logger.info(
                "Category created successfully",
                extra={"category_id": category.id, "store_id": store_id},
            )
            return category
        except Exception as e:
            logger.error(
                "Failed to create category",
                extra={"store_id": store_id, "error": str(e)},
            )
            raise

    async def get_categories(
        self, store_id: int, db: AsyncSession
    ) -> list[Category]:
        """Get all categories for a store.

        Args:
            store_id: The store ID.
            db: Database session.

        Returns:
            List of categories ordered by display_order.
        """
        return await self.repo.get_by_store(store_id=store_id, db=db)

    async def update_category(
        self, category_id: int, store_id: int, data: CategoryUpdate, db: AsyncSession
    ) -> Category:
        """Update a category.

        Args:
            category_id: The category ID.
            store_id: The store ID (for scope verification).
            data: Category update data.
            db: Database session.

        Returns:
            The updated category.

        Raises:
            HTTPException: If category not found or scope mismatch.
        """
        category = await self._get_category_with_scope_check(
            category_id, store_id, db
        )
        try:
            updated = await self.repo.update(
                category=category, name=data.name, db=db
            )
            logger.info(
                "Category updated successfully",
                extra={"category_id": category_id},
            )
            return updated
        except Exception as e:
            logger.error(
                "Failed to update category",
                extra={"category_id": category_id, "error": str(e)},
            )
            raise

    async def delete_category(
        self, category_id: int, store_id: int, db: AsyncSession
    ) -> None:
        """Delete a category.

        BR-CAT-02: Cannot delete if menus exist (409 Conflict).

        Args:
            category_id: The category ID.
            store_id: The store ID (for scope verification).
            db: Database session.

        Raises:
            HTTPException: If category not found, scope mismatch, or menus exist.
        """
        category = await self._get_category_with_scope_check(
            category_id, store_id, db
        )

        # BR-CAT-02: Check if category has menus
        menu_count = await self.repo.count_menus(category_id=category_id, db=db)
        if menu_count > 0:
            logger.warning(
                "Cannot delete category with existing menus",
                extra={"category_id": category_id, "menu_count": menu_count},
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"카테고리에 {menu_count}개의 메뉴가 존재합니다. 메뉴를 먼저 삭제해주세요.",
            )

        try:
            await self.repo.delete(category=category, db=db)
            logger.info(
                "Category deleted successfully",
                extra={"category_id": category_id, "store_id": store_id},
            )
        except Exception as e:
            logger.error(
                "Failed to delete category",
                extra={"category_id": category_id, "error": str(e)},
            )
            raise

    async def _get_category_with_scope_check(
        self, category_id: int, store_id: int, db: AsyncSession
    ) -> Category:
        """Get a category and verify it belongs to the given store.

        SECURITY-08: Object-level authorization (IDOR prevention).

        Args:
            category_id: The category ID.
            store_id: The expected store ID.
            db: Database session.

        Returns:
            The category.

        Raises:
            HTTPException: If not found or scope mismatch.
        """
        category = await self.repo.get_by_id(category_id=category_id, db=db)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다.",
            )
        if category.store_id != store_id:
            logger.warning(
                "Store scope mismatch for category access",
                extra={
                    "category_id": category_id,
                    "expected_store": store_id,
                    "actual_store": category.store_id,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 카테고리에 대한 접근 권한이 없습니다.",
            )
        return category
