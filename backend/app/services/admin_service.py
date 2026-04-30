"""관리자 서비스."""

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.repositories.admin_repo import AdminRepository
from app.repositories.store_repo import StoreRepository
from app.schemas.admin import AdminCreate, AdminUpdate
from app.utils.security import hash_password

logger = structlog.get_logger()


class AdminService:
    def __init__(self, session: AsyncSession):
        self.admin_repo = AdminRepository(session)
        self.store_repo = StoreRepository(session)

    async def get_by_store(self, store_id: int) -> list[Admin]:
        store = await self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="매장을 찾을 수 없습니다.")
        return await self.admin_repo.get_by_store_id(store_id)

    async def create(self, store_id: int, data: AdminCreate) -> Admin:
        # 매장 존재 확인
        store = await self.store_repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="매장을 찾을 수 없습니다.")

        # username 중복 확인
        existing = await self.admin_repo.get_by_store_and_username(store_id, data.username)
        if existing:
            raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")

        admin = Admin(
            store_id=store_id,
            username=data.username,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        admin = await self.admin_repo.create(admin)
        logger.info("admin_created", admin_id=admin.id, store_id=store_id)
        return admin

    async def update_status(self, admin_id: int, is_active: bool, current_admin_id: int) -> Admin:
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="관리자를 찾을 수 없습니다.")

        # 자기 자신 비활성화 방지
        if admin.id == current_admin_id and not is_active:
            raise HTTPException(status_code=400, detail="자기 자신을 비활성화할 수 없습니다.")

        admin.is_active = is_active
        admin = await self.admin_repo.update(admin)
        logger.info("admin_status_updated", admin_id=admin.id, is_active=is_active)
        return admin

    async def update(self, admin_id: int, data: AdminUpdate) -> Admin:
        admin = await self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="관리자를 찾을 수 없습니다.")

        if data.password is not None:
            admin.password_hash = hash_password(data.password)
        if data.is_active is not None:
            admin.is_active = data.is_active

        admin = await self.admin_repo.update(admin)
        logger.info("admin_updated", admin_id=admin.id)
        return admin
