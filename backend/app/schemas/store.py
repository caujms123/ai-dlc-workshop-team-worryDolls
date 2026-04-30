"""매장 관련 Pydantic 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field


class StoreCreate(BaseModel):
    """매장 등록 요청."""
    store_code: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-z0-9-]+$")
    name: str = Field(..., min_length=2, max_length=100)
    address: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)


class StoreUpdate(BaseModel):
    """매장 수정 요청."""
    name: str | None = Field(None, min_length=2, max_length=100)
    address: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class StoreResponse(BaseModel):
    """매장 응답."""
    id: int
    store_code: str
    name: str
    address: str | None = None
    phone: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
