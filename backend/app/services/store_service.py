"""매장 서비스."""

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store
from app.repositories.store_repo import StoreRepository
from app.schemas.store import StoreCreate, StoreUpdate

logger = structlog.get_logger()


class StoreService:
    def __init__(self, session: AsyncSession):
        self.repo = StoreRepository(session)

    async def get_all(self) -> list[Store]:
        return await self.repo.get_all()

    async def get_by_id(self, store_id: int) -> Store:
        store = await self.repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="매장을 찾을 수 없습니다.")
        return store

    async def create(self, data: StoreCreate) -> Store:
        # store_code 고유성 확인
        existing = await self.repo.get_by_code(data.store_code)
        if existing:
            raise HTTPException(status_code=409, detail="이미 사용 중인 매장 코드입니다.")

        store = Store(
            store_code=data.store_code,
            name=data.name,
            address=data.address,
            phone=data.phone,
        )
        store = await self.repo.create(store)
        logger.info("store_created", store_id=store.id, store_code=store.store_code)
        return store

    async def update(self, store_id: int, data: StoreUpdate) -> Store:
        store = await self.get_by_id(store_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(store, key, value)

        store = await self.repo.update(store)
        logger.info("store_updated", store_id=store.id)
        return store
