"""인증 미들웨어 및 의존성."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import UserInfo
from app.utils.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> UserInfo:
    """JWT 토큰에서 현재 사용자 정보 추출."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return UserInfo(
        id=int(payload["sub"]),
        role=payload["role"],
        store_id=payload.get("store_id"),
        username=payload.get("username"),
    )


def require_role(*roles: str):
    """역할 기반 접근 제어 의존성 팩토리."""
    async def _check_role(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        return current_user
    return Depends(_check_role)


def require_store_access():
    """매장 스코프 접근 제어 의존성."""
    async def _check_store(
        store_id: int,
        current_user: UserInfo = Depends(get_current_user),
    ) -> UserInfo:
        if current_user.role == "SUPER_ADMIN":
            return current_user
        if current_user.store_id != store_id:
            raise HTTPException(status_code=403, detail="해당 매장에 대한 접근 권한이 없습니다.")
        return current_user
    return Depends(_check_store)
