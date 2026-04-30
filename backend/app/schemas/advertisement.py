"""광고 관련 Pydantic 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field


class AdvertisementResponse(BaseModel):
    """광고 응답."""
    id: int
    store_id: int
    image_path: str
    display_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdvertisementOrderUpdate(BaseModel):
    """광고 순서 변경 요청."""
    display_order: int = Field(..., ge=0)


class AdvertisementStatusUpdate(BaseModel):
    """광고 활성/비활성 상태 변경."""
    is_active: bool
