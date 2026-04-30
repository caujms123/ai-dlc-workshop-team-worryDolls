"""인증/인가 미들웨어 (Unit 1에서 완성 예정).

Unit 3에서는 의존성 주입용 인터페이스만 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


@dataclass
class CurrentUser:
    """현재 인증된 사용자 정보."""

    user_id: int
    role: str  # SUPER_ADMIN, STORE_ADMIN, TABLE
    store_id: Optional[int] = None
    table_id: Optional[int] = None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """JWT 토큰에서 현재 사용자 정보 추출.

    Unit 1에서 실제 JWT 검증 로직으로 교체 예정.
    현재는 토큰 존재 여부만 확인합니다.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")

    # TODO: Unit 1에서 실제 JWT 디코딩 구현
    # 현재는 stub으로 동작
    try:
        # 실제 구현 시 jwt.decode(token, ...) 사용
        return CurrentUser(user_id=0, role="UNKNOWN")
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")


def require_role(*roles: str):
    """역할 기반 접근 제어 의존성 팩토리.

    사용 예:
        @router.get("/admin-only")
        async def admin_endpoint(user: CurrentUser = Depends(require_role("STORE_ADMIN"))):
            ...
    """

    async def role_checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"권한이 없습니다. 필요한 역할: {', '.join(roles)}",
            )
        return current_user

    return role_checker
