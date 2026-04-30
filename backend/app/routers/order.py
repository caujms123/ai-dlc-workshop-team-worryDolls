"""주문 API 라우터.

엔드포인트:
- POST   /api/orders                        - 주문 생성 (TABLE)
- GET    /api/tables/{table_id}/orders       - 테이블 현재 세션 주문 조회 (TABLE)
- GET    /api/stores/{store_id}/orders       - 매장 전체 주문 조회 (STORE_ADMIN)
- PATCH  /api/orders/{order_id}/status       - 주문 상태 변경 (STORE_ADMIN)
- DELETE /api/orders/{order_id}              - 주문 삭제 (STORE_ADMIN)
- POST   /api/tables/{table_id}/complete     - 이용 완료 처리 (STORE_ADMIN)
- GET    /api/tables/{table_id}/order-history - 과거 주문 내역 (STORE_ADMIN)
"""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import CurrentUser, require_role
from app.schemas.order import (
    OrderCreate,
    OrderHistoryResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["orders"])

# 서비스 인스턴스 (앱 시작 시 의존성 주입으로 교체 가능)
_order_service: Optional[OrderService] = None


def get_order_service() -> OrderService:
    """OrderService 의존성."""
    global _order_service
    if _order_service is None:
        _order_service = OrderService()
    return _order_service


# ── POST /api/orders - 주문 생성 (US-CU-09) ──


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=201,
    summary="주문 생성",
    description="고객이 장바구니 항목으로 주문을 생성합니다.",
)
async def create_order(
    order_data: OrderCreate,
    current_user: CurrentUser = Depends(require_role("TABLE")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """주문 생성 엔드포인트.

    - 테이블 역할(TABLE) 인증 필요
    - 주문 항목 1개 이상 필수
    - 결제 방식 (DUTCH_PAY / SINGLE_PAY) 필수
    """
    store_id = current_user.store_id
    if store_id is None:
        raise HTTPException(status_code=400, detail="매장 정보가 없습니다")

    order = await service.create_order(order_data, store_id, db)
    logger.info(
        "주문 생성 API: order_number=%s, user_id=%s",
        order.order_number,
        current_user.user_id,
    )
    return order


# ── GET /api/tables/{table_id}/orders - 테이블 현재 세션 주문 조회 (US-CU-10) ──


@router.get(
    "/tables/{table_id}/orders",
    response_model=list[OrderResponse],
    summary="테이블 현재 세션 주문 조회",
    description="현재 테이블 세션의 주문 목록을 조회합니다.",
)
async def get_table_orders(
    table_id: int,
    session_id: int = Query(..., gt=0, description="현재 세션 ID"),
    current_user: CurrentUser = Depends(require_role("TABLE", "STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """테이블 현재 세션 주문 조회 엔드포인트."""
    orders = await service.get_table_orders(table_id, session_id, db)
    return orders


# ── GET /api/stores/{store_id}/orders - 매장 전체 주문 조회 (US-MA-07) ──


@router.get(
    "/stores/{store_id}/orders",
    response_model=list[OrderResponse],
    summary="매장 전체 주문 조회",
    description="매장의 모든 활성 주문을 조회합니다 (관리자 대시보드용).",
)
async def get_store_orders(
    store_id: int,
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """매장 전체 주문 조회 엔드포인트.

    - 매장 관리자(STORE_ADMIN) 인증 필요
    - 자기 매장의 주문만 조회 가능
    """
    if current_user.store_id != store_id:
        raise HTTPException(status_code=403, detail="해당 매장의 주문만 조회할 수 있습니다")
    orders = await service.get_store_orders(store_id, db)
    return orders


# ── PATCH /api/orders/{order_id}/status - 주문 상태 변경 (US-MA-09) ──


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="주문 상태 변경",
    description="주문 상태를 변경합니다 (PENDING→PREPARING→COMPLETED).",
)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """주문 상태 변경 엔드포인트.

    - 매장 관리자(STORE_ADMIN) 인증 필요
    - 유효한 상태 전이만 허용
    """
    store_id = current_user.store_id
    if store_id is None:
        raise HTTPException(status_code=400, detail="매장 정보가 없습니다")

    order = await service.update_order_status(
        order_id, status_data.status, store_id, db
    )
    logger.info(
        "주문 상태 변경 API: order_id=%s, new_status=%s",
        order_id,
        status_data.status,
    )
    return order


# ── DELETE /api/orders/{order_id} - 주문 삭제 (US-MA-11) ──


@router.delete(
    "/orders/{order_id}",
    status_code=204,
    summary="주문 삭제",
    description="주문을 삭제합니다 (관리자 직권).",
)
async def delete_order(
    order_id: int,
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """주문 삭제 엔드포인트.

    - 매장 관리자(STORE_ADMIN) 인증 필요
    - 자기 매장의 주문만 삭제 가능
    """
    store_id = current_user.store_id
    if store_id is None:
        raise HTTPException(status_code=400, detail="매장 정보가 없습니다")

    await service.delete_order(order_id, store_id, db)
    logger.info("주문 삭제 API: order_id=%s, user_id=%s", order_id, current_user.user_id)


# ── POST /api/tables/{table_id}/complete - 이용 완료 처리 (US-MA-12) ──


@router.post(
    "/tables/{table_id}/complete",
    summary="테이블 이용 완료 처리",
    description="테이블 이용 완료 처리. 주문을 이력으로 이동합니다.",
)
async def complete_table(
    table_id: int,
    session_id: int = Query(..., gt=0, description="현재 세션 ID"),
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """테이블 이용 완료 엔드포인트.

    - 매장 관리자(STORE_ADMIN) 인증 필요
    - 해당 세션의 모든 주문을 OrderHistory로 이동
    """
    store_id = current_user.store_id
    if store_id is None:
        raise HTTPException(status_code=400, detail="매장 정보가 없습니다")

    moved_count = await service.move_to_history(session_id, store_id, db)
    logger.info(
        "이용 완료 API: table_id=%s, session_id=%s, moved=%s",
        table_id,
        session_id,
        moved_count,
    )
    return {"message": "이용 완료 처리되었습니다", "moved_orders": moved_count}


# ── GET /api/tables/{table_id}/order-history - 과거 주문 내역 (US-MA-13) ──


@router.get(
    "/tables/{table_id}/order-history",
    response_model=list[OrderHistoryResponse],
    summary="과거 주문 내역 조회",
    description="테이블의 과거 주문 이력을 조회합니다.",
)
async def get_order_history(
    table_id: int,
    date_from: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
    db: AsyncSession = Depends(get_db),
    service: OrderService = Depends(get_order_service),
):
    """과거 주문 내역 조회 엔드포인트.

    - 매장 관리자(STORE_ADMIN) 인증 필요
    - 날짜 필터링 지원
    """
    parsed_from = date.fromisoformat(date_from) if date_from else None
    parsed_to = date.fromisoformat(date_to) if date_to else None

    history = await service.get_order_history(
        table_id, db, date_from=parsed_from, date_to=parsed_to
    )
    return history
