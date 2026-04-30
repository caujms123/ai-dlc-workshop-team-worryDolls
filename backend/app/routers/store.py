"""매장 라우터."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.schemas.auth import UserInfo
from app.schemas.store import StoreCreate, StoreResponse, StoreUpdate
from app.services.store_service import StoreService

router = APIRouter(prefix="/api/stores", tags=["매장"])


@router.get("", response_model=list[StoreResponse])
async def get_stores(
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장 목록 조회 (슈퍼 관리자 전용)."""
    service = StoreService(db)
    return await service.get_all()


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장 상세 조회."""
    service = StoreService(db)
    return await service.get_by_id(store_id)


@router.post("", response_model=StoreResponse, status_code=201)
async def create_store(
    data: StoreCreate,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장 등록 (슈퍼 관리자 전용)."""
    service = StoreService(db)
    return await service.create(data)


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    data: StoreUpdate,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장 수정 (슈퍼 관리자 전용)."""
    service = StoreService(db)
    return await service.update(store_id, data)
