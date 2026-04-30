"""Menu repository for database operations."""

import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import Menu

logger = logging.getLogger(__name__)


class MenuRepository:
    """Repository for Menu CRUD operations."""

    async def get_by_store(
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
            List of menus ordered by display_order.
        """
        stmt = (
            select(Menu)
            .where(Menu.store_id == store_id)
            .order_by(Menu.category_id, Menu.display_order)
        )
        if category_id is not None:
            stmt = stmt.where(Menu.category_id == category_id)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_available_by_store(
        self, store_id: int, db: AsyncSession
    ) -> list[Menu]:
        """Get available menus for a store (customer view).

        Args:
            store_id: The store ID.
            db: Database session.

        Returns:
            List of available menus ordered by category and display_order.
        """
        stmt = (
            select(Menu)
            .where(Menu.store_id == store_id, Menu.is_available.is_(True))
            .order_by(Menu.category_id, Menu.display_order)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_available_by_category(
        self, category_id: int, db: AsyncSession
    ) -> list[Menu]:
        """Get available menus for a specific category.

        Args:
            category_id: The category ID.
            db: Database session.

        Returns:
            List of available menus ordered by display_order.
        """
        stmt = (
            select(Menu)
            .where(Menu.category_id == category_id, Menu.is_available.is_(True))
            .order_by(Menu.display_order)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self, menu_id: int, db: AsyncSession
    ) -> Menu | None:
        """Get a menu by its ID.

        Args:
            menu_id: The menu ID.
            db: Database session.

        Returns:
            Menu if found, None otherwise.
        """
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        store_id: int,
        category_id: int,
        name: str,
        price: int,
        description: str | None,
        image_path: str | None,
        db: AsyncSession,
    ) -> Menu:
        """Create a new menu item with auto-assigned display_order.

        Args:
            store_id: The store ID.
            category_id: The category ID.
            name: Menu name.
            price: Menu price.
            description: Menu description.
            image_path: Image file path.
            db: Database session.

        Returns:
            The created menu.
        """
        # Auto-assign display_order (last + 1 within category)
        max_order_stmt = select(
            func.coalesce(func.max(Menu.display_order), -1)
        ).where(Menu.store_id == store_id, Menu.category_id == category_id)
        result = await db.execute(max_order_stmt)
        max_order = result.scalar_one()

        menu = Menu(
            store_id=store_id,
            category_id=category_id,
            name=name,
            price=price,
            description=description,
            image_path=image_path,
            display_order=max_order + 1,
        )
        db.add(menu)
        await db.flush()
        await db.refresh(menu)

        logger.info(
            "Menu created",
            extra={"menu_id": menu.id, "store_id": store_id, "name": name},
        )
        return menu

    async def update(self, menu: Menu, db: AsyncSession, **kwargs) -> Menu:
        """Update a menu item's fields.

        Args:
            menu: The menu to update.
            db: Database session.
            **kwargs: Fields to update.

        Returns:
            The updated menu.
        """
        for key, value in kwargs.items():
            if value is not None and hasattr(menu, key):
                setattr(menu, key, value)

        await db.flush()
        await db.refresh(menu)

        logger.info(
            "Menu updated",
            extra={"menu_id": menu.id, "updated_fields": list(kwargs.keys())},
        )
        return menu

    async def delete(self, menu: Menu, db: AsyncSession) -> None:
        """Delete a menu and reorder remaining menus in the same category.

        Args:
            menu: The menu to delete.
            db: Database session.
        """
        store_id = menu.store_id
        category_id = menu.category_id

        await db.delete(menu)
        await db.flush()

        # Reorder remaining menus in the same category
        remaining_stmt = (
            select(Menu)
            .where(Menu.store_id == store_id, Menu.category_id == category_id)
            .order_by(Menu.display_order)
        )
        result = await db.execute(remaining_stmt)
        remaining = list(result.scalars().all())

        for i, m in enumerate(remaining):
            if m.display_order != i:
                m.display_order = i
        await db.flush()

        logger.info(
            "Menu deleted and reordered",
            extra={"store_id": store_id, "category_id": category_id},
        )

    async def reorder(
        self,
        menu: Menu,
        new_order: int,
        db: AsyncSession,
    ) -> Menu:
        """Update a menu's display order and reorder siblings.

        Args:
            menu: The menu to reorder.
            new_order: The new display order.
            db: Database session.

        Returns:
            The reordered menu.
        """
        old_order = menu.display_order
        if old_order == new_order:
            return menu

        # Get all menus in the same category
        siblings_stmt = (
            select(Menu)
            .where(
                Menu.store_id == menu.store_id,
                Menu.category_id == menu.category_id,
                Menu.id != menu.id,
            )
            .order_by(Menu.display_order)
        )
        result = await db.execute(siblings_stmt)
        siblings = list(result.scalars().all())

        # Remove the menu from its current position and insert at new position
        siblings.insert(min(new_order, len(siblings)), menu)

        for i, m in enumerate(siblings):
            if m.display_order != i:
                m.display_order = i

        await db.flush()
        await db.refresh(menu)

        logger.info(
            "Menu reordered",
            extra={
                "menu_id": menu.id,
                "old_order": old_order,
                "new_order": new_order,
            },
        )
        return menu
