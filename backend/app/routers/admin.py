"""관리자 라우터."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.schemas.admin import AdminCreate, AdminResponse, AdminStatusUpdate
from app.schemas.auth import UserInfo
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api", tags=["관리자"])


@router.get("/stores/{store_id}/admins", response_model=list[AdminResponse])
async def get_admins_by_store(
    store_id: int,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """매장별 관리자 목록 조회 (슈퍼 관리자 전용)."""
    service = AdminService(db)
    return await service.get_by_store(store_id)


@router.post("/stores/{store_id}/admins", response_model=AdminResponse, status_code=201)
async def create_admin(
    store_id: int,
    data: AdminCreate,
    _user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """관리자 생성 (슈퍼 관리자 전용)."""
    service = AdminService(db)
    return await service.create(store_id, data)


@router.patch("/admins/{admin_id}/status", response_model=AdminResponse)
async def update_admin_status(
    admin_id: int,
    data: AdminStatusUpdate,
    user: UserInfo = require_role("SUPER_ADMIN"),
    db: AsyncSession = Depends(get_db),
):
    """관리자 활성/비활성 상태 변경 (슈퍼 관리자 전용)."""
    service = AdminService(db)
    return await service.update_status(admin_id, data.is_active, user.id)
