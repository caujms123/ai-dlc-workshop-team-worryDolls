"""광고 라우터."""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.schemas.advertisement import (
    AdvertisementOrderUpdate,
    AdvertisementResponse,
    AdvertisementStatusUpdate,
)
from app.schemas.auth import UserInfo
from app.services.ad_service import AdvertisementService

router = APIRouter(prefix="/api", tags=["광고"])


@router.get("/stores/{store_id}/advertisements", response_model=list[AdvertisementResponse])
async def get_advertisements(
    store_id: int,
    db: AsyncSession = Depends(get_db),
):
    """매장별 광고 목록 조회 (공개 - 고객 화면용)."""
    service = AdvertisementService(db)
    return await service.get_by_store(store_id, active_only=True)


@router.get(
    "/admin/stores/{store_id}/advertisements",
    response_model=list[AdvertisementResponse],
)
async def get_all_advertisements(
    store_id: int,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장별 광고 전체 목록 조회 (관리자용, 비활성 포함)."""
    service = AdvertisementService(db)
    return await service.get_by_store(store_id, active_only=False)


@router.post(
    "/stores/{store_id}/advertisements",
    response_model=AdvertisementResponse,
    status_code=201,
)
async def upload_advertisement(
    store_id: int,
    file: UploadFile = File(...),
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """광고 이미지 업로드 (슈퍼 관리자 전용)."""
    service = AdvertisementService(db)
    return await service.upload(store_id, file)


@router.put("/advertisements/{ad_id}/order", response_model=AdvertisementResponse)
async def update_ad_order(
    ad_id: int,
    data: AdvertisementOrderUpdate,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """광고 순서 변경 (슈퍼 관리자 전용)."""
    service = AdvertisementService(db)
    return await service.update_order(ad_id, data.display_order)


@router.patch("/advertisements/{ad_id}/status", response_model=AdvertisementResponse)
async def update_ad_status(
    ad_id: int,
    data: AdvertisementStatusUpdate,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """광고 활성/비활성 상태 변경 (슈퍼 관리자 전용)."""
    service = AdvertisementService(db)
    return await service.update_status(ad_id, data.is_active)


@router.delete("/advertisements/{ad_id}", status_code=204)
async def delete_advertisement(
    ad_id: int,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """광고 삭제 (슈퍼 관리자 전용)."""
    service = AdvertisementService(db)
    await service.delete(ad_id)
