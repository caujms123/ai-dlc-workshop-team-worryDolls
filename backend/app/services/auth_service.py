"""인증 서비스."""

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.admin_repo import AdminRepository
from app.repositories.login_attempt_repo import LoginAttemptRepository
from app.repositories.store_repo import StoreRepository
from app.config import settings
from app.utils.security import create_access_token, verify_password

logger = structlog.get_logger()


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.store_repo = StoreRepository(session)
        self.admin_repo = AdminRepository(session)
        self.attempt_repo = LoginAttemptRepository(session)

    async def login_admin(
        self, store_code: str | None, username: str, password: str
    ) -> dict:
        """관리자 로그인. 슈퍼 관리자는 store_code=None."""
        identifier = f"{store_code or 'super'}:{username}"

        # 로그인 시도 제한 확인
        await self._check_login_attempts(identifier)

        store_id: int | None = None
        if store_code:
            # 매장 관리자 로그인
            store = await self.store_repo.get_by_code(store_code)
            if not store or not store.is_active:
                await self._record_failed_attempt(identifier)
                raise HTTPException(status_code=401, detail="인증에 실패했습니다.")
            store_id = store.id

        # 관리자 조회
        admin = await self.admin_repo.get_by_store_and_username(store_id, username)
        if not admin or not admin.is_active:
            await self._record_failed_attempt(identifier)
            raise HTTPException(status_code=401, detail="인증에 실패했습니다.")

        # 비밀번호 검증
        if not verify_password(password, admin.password_hash):
            await self._record_failed_attempt(identifier)
            raise HTTPException(status_code=401, detail="인증에 실패했습니다.")

        # 성공: 시도 횟수 리셋
        await self.attempt_repo.reset(identifier)

        # JWT 토큰 생성
        token_data = {
            "sub": str(admin.id),
            "role": admin.role,
            "store_id": admin.store_id,
            "username": admin.username,
        }
        token, expires_in = create_access_token(token_data)

        logger.info("admin_login_success", admin_id=admin.id, role=admin.role, store_id=admin.store_id)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "role": admin.role,
            "store_id": admin.store_id,
        }

    async def _check_login_attempts(self, identifier: str) -> None:
        """로그인 시도 제한 확인."""
        attempt = await self.attempt_repo.get_by_identifier(identifier)
        if attempt and attempt.locked_until:
            now = datetime.now(timezone.utc)
            if now < attempt.locked_until.replace(tzinfo=timezone.utc):
                logger.warning("login_locked", identifier=identifier)
                raise HTTPException(
                    status_code=429,
                    detail="로그인 시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.",
                )
            # 잠금 해제 시간 경과 → 리셋
            await self.attempt_repo.reset(identifier)

    async def _record_failed_attempt(self, identifier: str) -> None:
        """실패한 로그인 시도 기록."""
        attempt = await self.attempt_repo.create_or_increment(identifier)
        if attempt.attempt_count >= settings.LOGIN_MAX_ATTEMPTS:
            locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.LOGIN_LOCKOUT_MINUTES
            )
            await self.attempt_repo.lock(identifier, locked_until)
            logger.warning("login_locked_due_to_attempts", identifier=identifier)
