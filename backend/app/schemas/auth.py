"""인증 관련 Pydantic 스키마."""

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """관리자 로그인 요청."""
    store_code: str | None = Field(None, min_length=3, max_length=30, description="매장 코드 (매장 관리자만)")
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)


class TableLoginRequest(BaseModel):
    """테이블 로그인 요청."""
    store_code: str = Field(..., min_length=3, max_length=30)
    table_number: int = Field(..., gt=0)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """토큰 응답."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    store_id: int | None = None


class UserInfo(BaseModel):
    """JWT에서 추출한 사용자 정보."""
    id: int
    role: str
    store_id: int | None = None
    username: str | None = None
