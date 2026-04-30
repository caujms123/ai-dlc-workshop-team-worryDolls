"""SSE 이벤트 스키마 정의."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SSEEvent(BaseModel):
    """SSE 이벤트 기본 스키마."""

    event_type: str = Field(..., description="이벤트 유형")
    data: dict[str, Any] = Field(default_factory=dict, description="이벤트 데이터")


class NewOrderEvent(BaseModel):
    """신규 주문 SSE 이벤트 데이터."""

    order_id: int
    order_number: str
    table_id: int
    table_number: int = 0
    total_amount: int
    items_preview: str
    status: str
    ordered_at: str


class OrderStatusChangedEvent(BaseModel):
    """주문 상태 변경 SSE 이벤트 데이터."""

    order_id: int
    order_number: str
    table_id: int
    previous_status: str
    new_status: str


class OrderDeletedEvent(BaseModel):
    """주문 삭제 SSE 이벤트 데이터."""

    order_id: int
    table_id: int
    order_number: str


class TableCompletedEvent(BaseModel):
    """테이블 이용 완료 SSE 이벤트 데이터."""

    table_id: int
    table_number: int = 0
    completed_orders_count: int
