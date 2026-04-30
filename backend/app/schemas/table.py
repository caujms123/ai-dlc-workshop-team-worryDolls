"""테이블 Pydantic 스키마 (Unit 4)"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Request Schemas ---

class TableCreate(BaseModel):
    """테이블 등록 요청"""
    table_number: int = Field(..., gt=0, description="테이블 번호 (양수)")
    password: str = Field(..., min_length=4, max_length=50, description="테이블 비밀번호 (최소 4자)")


class TableUpdate(BaseModel):
    """테이블 수정 요청"""
    password: Optional[str] = Field(None, min_length=4, max_length=50, description="새 비밀번호")


# --- Response Schemas ---

class TableResponse(BaseModel):
    """테이블 응답"""
    id: int
    store_id: int
    table_number: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TableSessionResponse(BaseModel):
    """테이블 세션 응답"""
    id: int
    table_id: int
    store_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class TableWithSessionResponse(BaseModel):
    """테이블 + 현재 세션 정보 응답"""
    id: int
    store_id: int
    table_number: int
    is_active: bool
    current_session: Optional[TableSessionResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompleteTableResponse(BaseModel):
    """이용 완료 응답"""
    message: str = "이용 완료 처리되었습니다."
    table_id: int
    session_id: int
