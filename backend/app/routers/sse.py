"""SSE (Server-Sent Events) API 라우터.

엔드포인트:
- GET /api/sse/admin/stores/{store_id}/orders  - 관리자 주문 SSE 스트림
- GET /api/sse/customer/tables/{table_id}/orders - 고객 주문 상태 SSE 스트림
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.middleware.auth import CurrentUser, require_role
from app.services.sse_service import sse_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sse", tags=["sse"])

KEEP_ALIVE_INTERVAL = 30  # 초


async def _event_generator(queue: asyncio.Queue):
    """SSE 이벤트 제너레이터.

    - 이벤트 수신 시 SSE 형식으로 전송
    - 30초 타임아웃 시 keep-alive ping 전송
    """
    try:
        while True:
            try:
                event = await asyncio.wait_for(
                    queue.get(), timeout=KEEP_ALIVE_INTERVAL
                )
                event_type = event.get("event_type", "message")
                data = json.dumps(event.get("data", event), ensure_ascii=False)
                yield f"event: {event_type}\ndata: {data}\n\n"
            except asyncio.TimeoutError:
                # keep-alive ping
                yield ": keep-alive\n\n"
    except asyncio.CancelledError:
        logger.info("SSE 연결 종료 (클라이언트 연결 해제)")
        raise


# ── GET /api/sse/admin/stores/{store_id}/orders - 관리자 SSE (US-MA-07) ──


@router.get(
    "/admin/stores/{store_id}/orders",
    summary="관리자 주문 SSE 스트림",
    description="매장의 주문 이벤트를 실시간으로 수신합니다.",
)
async def admin_order_stream(
    store_id: int,
    current_user: CurrentUser = Depends(require_role("STORE_ADMIN")),
):
    """관리자 주문 SSE 스트림 엔드포인트.

    이벤트 유형:
    - new_order: 신규 주문
    - order_status_changed: 주문 상태 변경
    - order_deleted: 주문 삭제
    - table_completed: 테이블 이용 완료
    """
    # 매장 스코프 검증
    if current_user.store_id != store_id:
        raise HTTPException(
            status_code=403, detail="해당 매장의 SSE 스트림에 접근할 수 없습니다"
        )

    try:
        queue = await sse_manager.subscribe_admin(store_id)
    except ConnectionError as e:
        raise HTTPException(status_code=429, detail=str(e))

    logger.info(
        "관리자 SSE 연결: store_id=%s, user_id=%s",
        store_id,
        current_user.user_id,
    )

    async def stream_with_cleanup():
        try:
            async for event in _event_generator(queue):
                yield event
        finally:
            await sse_manager.unsubscribe_admin(store_id, queue)
            logger.info("관리자 SSE 연결 해제: store_id=%s", store_id)

    return StreamingResponse(
        stream_with_cleanup(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── GET /api/sse/customer/tables/{table_id}/orders - 고객 SSE (US-CU-10) ──


@router.get(
    "/customer/tables/{table_id}/orders",
    summary="고객 주문 상태 SSE 스트림",
    description="테이블의 주문 상태 변경을 실시간으로 수신합니다.",
)
async def customer_order_stream(
    table_id: int,
    current_user: CurrentUser = Depends(require_role("TABLE")),
):
    """고객 주문 상태 SSE 스트림 엔드포인트.

    이벤트 유형:
    - order_status_changed: 주문 상태 변경
    """
    # 테이블 스코프 검증
    if current_user.table_id != table_id:
        raise HTTPException(
            status_code=403, detail="해당 테이블의 SSE 스트림에 접근할 수 없습니다"
        )

    try:
        queue = await sse_manager.subscribe_customer(table_id)
    except ConnectionError as e:
        raise HTTPException(status_code=429, detail=str(e))

    logger.info("고객 SSE 연결: table_id=%s", table_id)

    async def stream_with_cleanup():
        try:
            async for event in _event_generator(queue):
                yield event
        finally:
            await sse_manager.unsubscribe_customer(table_id, queue)
            logger.info("고객 SSE 연결 해제: table_id=%s", table_id)

    return StreamingResponse(
        stream_with_cleanup(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
