"""광고 리포지토리."""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advertisement import Advertisement


class AdvertisementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, ad_id: int) -> Advertisement | None:
        return await self.session.get(Advertisement, ad_id)

    async def get_by_store_id(self, store_id: int, active_only: bool = False) -> list[Advertisement]:
        query = select(Advertisement).where(Advertisement.store_id == store_id)
        if active_only:
            query = query.where(Advertisement.is_active.is_(True))
        query = query.order_by(Advertisement.display_order)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_max_order(self, store_id: int) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(Advertisement.display_order), -1)).where(
                Advertisement.store_id == store_id
            )
        )
        return result.scalar_one()

    async def create(self, ad: Advertisement) -> Advertisement:
        self.session.add(ad)
        await self.session.flush()
        await self.session.refresh(ad)
        return ad

    async def update(self, ad: Advertisement) -> Advertisement:
        await self.session.flush()
        await self.session.refresh(ad)
        return ad

    async def delete(self, ad: Advertisement) -> None:
        await self.session.delete(ad)
        await self.session.flush()
