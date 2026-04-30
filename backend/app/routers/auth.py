"""인증 라우터."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.auth import AdminLoginRequest, TokenResponse, UserInfo
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """관리자 로그인 (슈퍼 관리자 / 매장 관리자)."""
    service = AuthService(db)
    result = await service.login_admin(
        store_code=request.store_code,
        username=request.username,
        password=request.password,
    )
    return result


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회."""
    return current_user


@router.post("/logout")
async def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)."""
    return {"message": "로그아웃 되었습니다."}
