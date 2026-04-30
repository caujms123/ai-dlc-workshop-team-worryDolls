"""매장 리포지토리."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store


class StoreRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, store_id: int) -> Store | None:
        return await self.session.get(Store, store_id)

    async def get_by_code(self, store_code: str) -> Store | None:
        result = await self.session.execute(
            select(Store).where(Store.store_code == store_code)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Store]:
        result = await self.session.execute(select(Store).order_by(Store.id))
        return list(result.scalars().all())

    async def create(self, store: Store) -> Store:
        self.session.add(store)
        await self.session.flush()
        await self.session.refresh(store)
        return store

    async def update(self, store: Store) -> Store:
        await self.session.flush()
        await self.session.refresh(store)
        return store
