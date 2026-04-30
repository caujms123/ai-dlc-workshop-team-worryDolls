"""주문 관련 Pydantic 스키마 정의."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class OrderItemCreate(BaseModel):
    """주문 항목 생성 요청."""

    menu_id: int = Field(..., gt=0, description="메뉴 ID")
    quantity: int = Field(..., gt=0, le=99, description="수량 (1~99)")


class OrderCreate(BaseModel):
    """주문 생성 요청."""

    table_id: int = Field(..., gt=0, description="테이블 ID")
    payment_type: str = Field(..., description="결제 방식 (DUTCH_PAY | SINGLE_PAY)")
    items: list[OrderItemCreate] = Field(
        ..., min_length=1, max_length=50, description="주문 항목 목록"
    )

    @field_validator("payment_type")
    @classmethod
    def validate_payment_type(cls, v: str) -> str:
        """결제 방식 검증."""
        allowed = {"DUTCH_PAY", "SINGLE_PAY"}
        if v not in allowed:
            raise ValueError(f"결제 방식은 {allowed} 중 하나여야 합니다")
        return v


class OrderStatusUpdate(BaseModel):
    """주문 상태 변경 요청."""

    status: str = Field(..., description="새 상태 (PENDING | PREPARING | COMPLETED)")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """상태값 검증."""
        allowed = {"PENDING", "PREPARING", "COMPLETED"}
        if v not in allowed:
            raise ValueError(f"상태는 {allowed} 중 하나여야 합니다")
        return v


class OrderItemResponse(BaseModel):
    """주문 항목 응답."""

    id: int
    order_id: int
    menu_id: int
    menu_name: str
    quantity: int
    unit_price: int
    subtotal: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """주문 응답."""

    id: int
    order_number: str
    store_id: int
    table_id: int
    session_id: int
    status: str
    payment_type: str
    total_amount: int
    ordered_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderHistoryResponse(BaseModel):
    """과거 주문 이력 응답."""

    id: int
    original_order_id: int
    order_number: str
    store_id: int
    table_id: int
    session_id: int
    status: str
    payment_type: str
    total_amount: int
    items_json: list[dict]
    ordered_at: datetime
    completed_at: datetime

    model_config = {"from_attributes": True}


class TableOrderSummary(BaseModel):
    """테이블별 주문 요약 (관리자 대시보드용)."""

    table_id: int
    table_number: int
    total_amount: int
    order_count: int
    latest_orders: list[OrderResponse] = []


class StoreOrdersResponse(BaseModel):
    """매장 전체 주문 응답 (관리자 대시보드용)."""

    tables: list[TableOrderSummary] = []


class OrderHistoryQuery(BaseModel):
    """과거 주문 이력 조회 쿼리."""

    date_from: Optional[str] = Field(None, description="시작 날짜 (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="종료 날짜 (YYYY-MM-DD)")
