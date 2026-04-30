"""관리자 리포지토리."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, admin_id: int) -> Admin | None:
        return await self.session.get(Admin, admin_id)

    async def get_by_store_and_username(self, store_id: int | None, username: str) -> Admin | None:
        if store_id is None:
            result = await self.session.execute(
                select(Admin).where(Admin.store_id.is_(None), Admin.username == username)
            )
        else:
            result = await self.session.execute(
                select(Admin).where(Admin.store_id == store_id, Admin.username == username)
            )
        return result.scalar_one_or_none()

    async def get_by_store_id(self, store_id: int) -> list[Admin]:
        result = await self.session.execute(
            select(Admin).where(Admin.store_id == store_id).order_by(Admin.id)
        )
        return list(result.scalars().all())

    async def get_super_admins(self) -> list[Admin]:
        result = await self.session.execute(
            select(Admin).where(Admin.role == "SUPER_ADMIN").order_by(Admin.id)
        )
        return list(result.scalars().all())

    async def create(self, admin: Admin) -> Admin:
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)
        return admin

    async def update(self, admin: Admin) -> Admin:
        await self.session.flush()
        await self.session.refresh(admin)
        return admin
