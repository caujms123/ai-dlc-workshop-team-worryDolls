"""광고 서비스."""

import structlog
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advertisement import Advertisement
from app.repositories.ad_repo import AdvertisementRepository
from app.repositories.store_repo import StoreRepository
from app.utils.file_utils import delete_image, save_image, validate_image

logger = structlog.get_logger()


class AdvertisementService:
    def __init__(self, session: AsyncSession):
        self.ad_repo = AdvertisementRepository(session)
        self.store_repo = StoreRepository(session)

    async def get_by_store(self, store_id: int, active_only: bool = False) -> list[Advertisement]:
        return await self.ad_repo.get_by_store_id(store_id, active_only=active_only)

    async def upload(self, store_id: int, file: UploadFile) -> Advertisement:
        # 매장 존재 확인
        store = await self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="매장을 찾을 수 없습니다.")

        # 이미지 검증
        content = await validate_image(file)

        # 파일 저장
        image_path = await save_image(content, "advertisements", store_id, file.filename or "image.jpg")

        # DB 저장
        max_order = await self.ad_repo.get_max_order(store_id)
        ad = Advertisement(
            store_id=store_id,
            image_path=image_path,
            display_order=max_order + 1,
        )
        ad = await self.ad_repo.create(ad)
        logger.info("ad_uploaded", ad_id=ad.id, store_id=store_id)
        return ad

    async def update_order(self, ad_id: int, display_order: int) -> Advertisement:
        ad = await self.ad_repo.get_by_id(ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="광고를 찾을 수 없습니다.")
        ad.display_order = display_order
        ad = await self.ad_repo.update(ad)
        return ad

    async def update_status(self, ad_id: int, is_active: bool) -> Advertisement:
        ad = await self.ad_repo.get_by_id(ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="광고를 찾을 수 없습니다.")
        ad.is_active = is_active
        ad = await self.ad_repo.update(ad)
        logger.info("ad_status_updated", ad_id=ad.id, is_active=is_active)
        return ad

    async def delete(self, ad_id: int) -> None:
        ad = await self.ad_repo.get_by_id(ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="광고를 찾을 수 없습니다.")

        # 파일 삭제
        await delete_image(ad.image_path)

        store_id = ad.store_id
        await self.ad_repo.delete(ad)

        # 나머지 광고 display_order 재정렬
        remaining = await self.ad_repo.get_by_store_id(store_id)
        for idx, remaining_ad in enumerate(remaining):
            remaining_ad.display_order = idx

        logger.info("ad_deleted", ad_id=ad_id, store_id=store_id)
