"""Category repository for database operations."""

import logging

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.category import Category

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Repository for Category CRUD operations."""

    async def get_by_store(
        self, store_id: int, db: AsyncSession
    ) -> list[Category]:
        """Get all categories for a store, ordered by display_order.

        Args:
            store_id: The store ID.
            db: Database session.

        Returns:
            List of categories ordered by display_order.
        """
        stmt = (
            select(Category)
            .where(Category.store_id == store_id)
            .order_by(Category.display_order)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self, category_id: int, db: AsyncSession
    ) -> Category | None:
        """Get a category by its ID.

        Args:
            category_id: The category ID.
            db: Database session.

        Returns:
            Category if found, None otherwise.
        """
        stmt = select(Category).where(Category.id == category_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, store_id: int, name: str, db: AsyncSession
    ) -> Category:
        """Create a new category with auto-assigned display_order.

        Args:
            store_id: The store ID.
            name: Category name.
            db: Database session.

        Returns:
            The created category.
        """
        # Auto-assign display_order (last + 1)
        max_order_stmt = select(func.coalesce(func.max(Category.display_order), -1)).where(
            Category.store_id == store_id
        )
        result = await db.execute(max_order_stmt)
        max_order = result.scalar_one()

        category = Category(
            store_id=store_id,
            name=name,
            display_order=max_order + 1,
        )
        db.add(category)
        await db.flush()
        await db.refresh(category)

        logger.info(
            "Category created",
            extra={"category_id": category.id, "store_id": store_id, "name": name},
        )
        return category

    async def update(
        self, category: Category, name: str, db: AsyncSession
    ) -> Category:
        """Update a category's name.

        Args:
            category: The category to update.
            name: New category name.
            db: Database session.

        Returns:
            The updated category.
        """
        category.name = name
        await db.flush()
        await db.refresh(category)

        logger.info(
            "Category updated",
            extra={"category_id": category.id, "name": name},
        )
        return category

    async def delete(self, category: Category, db: AsyncSession) -> None:
        """Delete a category and reorder remaining categories.

        Args:
            category: The category to delete.
            db: Database session.
        """
        store_id = category.store_id
        deleted_order = category.display_order

        await db.delete(category)
        await db.flush()

        # Reorder remaining categories
        remaining = await self.get_by_store(store_id, db)
        for i, cat in enumerate(remaining):
            if cat.display_order != i:
                cat.display_order = i
        await db.flush()

        logger.info(
            "Category deleted and reordered",
            extra={"store_id": store_id, "deleted_order": deleted_order},
        )

    async def count_menus(
        self, category_id: int, db: AsyncSession
    ) -> int:
        """Count the number of menus in a category.

        Args:
            category_id: The category ID.
            db: Database session.

        Returns:
            Number of menus in the category.
        """
        from backend.app.models.menu import Menu

        stmt = select(func.count()).where(Menu.category_id == category_id)
        result = await db.execute(stmt)
        return result.scalar_one()
