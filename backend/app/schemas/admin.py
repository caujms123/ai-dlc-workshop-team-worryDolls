"""관리자 관련 Pydantic 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    """관리자 생성 요청."""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)
    role: str = Field(default="STORE_ADMIN", pattern=r"^(SUPER_ADMIN|STORE_ADMIN)$")


class AdminUpdate(BaseModel):
    """관리자 수정 요청."""
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class AdminResponse(BaseModel):
    """관리자 응답 (password_hash 제외)."""
    id: int
    store_id: int | None = None
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminStatusUpdate(BaseModel):
    """관리자 활성/비활성 상태 변경."""
    is_active: bool
