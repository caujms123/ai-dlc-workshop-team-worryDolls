"""주문 비즈니스 로직 서비스.

주문 생성, 상태 변경, 삭제, 이력 관리, SSE 이벤트 발행을 담당합니다.
"""

import json
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import (
    Order,
    OrderHistory,
    OrderItem,
    OrderStatus,
    PaymentType,
    VALID_STATUS_TRANSITIONS,
)
from app.repositories.order_repo import OrderRepository
from app.schemas.order import OrderCreate, OrderItemCreate
from app.services.sse_service import sse_manager

logger = logging.getLogger(__name__)


class OrderService:
    """주문 비즈니스 로직 서비스."""

    def __init__(
        self,
        order_repo: Optional[OrderRepository] = None,
        menu_service=None,
        table_service=None,
    ) -> None:
        self.order_repo = order_repo or OrderRepository()
        self.menu_service = menu_service
        self.table_service = table_service

    # ── 주문 번호 생성 ──

    async def _generate_order_number(
        self, store_id: int, db: AsyncSession
    ) -> str:
        """주문 번호 생성: ORD-YYYYMMDD-NNNN (매장별 일일 순번)."""
        today_str = date.today().strftime("%Y%m%d")
        count = await self.order_repo.count_today_orders(store_id, today_str, db)
        order_number = f"ORD-{today_str}-{count + 1:04d}"
        logger.info("주문 번호 생성: %s (store_id=%s)", order_number, store_id)
        return order_number

    # ── 메뉴 검증 및 스냅샷 ──

    async def _validate_and_snapshot_items(
        self,
        items: list[OrderItemCreate],
        store_id: int,
        db: AsyncSession,
    ) -> list[dict]:
        """주문 항목의 메뉴 유효성 검증 및 가격 스냅샷 생성.

        Returns:
            [{"menu_id", "menu_name", "quantity", "unit_price", "subtotal"}, ...]

        Raises:
            HTTPException: 메뉴가 존재하지 않거나 비활성 또는 다른 매장인 경우
        """
        validated_items = []
        for item in items:
            # menu_service가 주입되지 않은 경우 (독립 테스트 등)
            if self.menu_service is None:
                raise HTTPException(
                    status_code=500,
                    detail="MenuService가 초기화되지 않았습니다",
                )
            menu = await self.menu_service.get_menu(item.menu_id, db)
            if menu is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"메뉴를 찾을 수 없습니다: menu_id={item.menu_id}",
                )
            if hasattr(menu, "store_id") and menu.store_id != store_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"해당 매장의 메뉴가 아닙니다: menu_id={item.menu_id}",
                )
            unit_price = menu.price if hasattr(menu, "price") else 0
            subtotal = item.quantity * unit_price
            validated_items.append({
                "menu_id": item.menu_id,
                "menu_name": menu.name if hasattr(menu, "name") else str(item.menu_id),
                "quantity": item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })
        return validated_items

    # ── 주문 생성 (US-CU-09) ──

    async def create_order(
        self,
        order_data: OrderCreate,
        store_id: int,
        db: AsyncSession,
    ) -> Order:
        """주문 생성.

        1. 세션 확인/시작
        2. 메뉴 유효성 검증 + 스냅샷
        3. 주문 번호 생성
        4. 금액 계산
        5. DB 저장 (트랜잭션)
        6. SSE 이벤트 발행

        Args:
            order_data: 주문 생성 요청 데이터
            store_id: 매장 ID (JWT에서 추출)
            db: DB 세션

        Returns:
            생성된 Order 객체

        Raises:
            HTTPException: 검증 실패 시
        """
        # 1. 세션 확인
        session = None
        if self.table_service:
            session = await self.table_service.get_or_create_session(
                order_data.table_id, db
            )
        session_id = session.id if session else 1  # fallback

        # 2. 메뉴 검증 + 스냅샷
        validated_items = await self._validate_and_snapshot_items(
            order_data.items, store_id, db
        )

        # 3. 주문 번호 생성
        order_number = await self._generate_order_number(store_id, db)

        # 4. 금액 계산
        total_amount = sum(item["subtotal"] for item in validated_items)

        # 5. DB 저장
        order = Order(
            order_number=order_number,
            store_id=store_id,
            table_id=order_data.table_id,
            session_id=session_id,
            status=OrderStatus.PENDING,
            payment_type=PaymentType(order_data.payment_type),
            total_amount=total_amount,
            ordered_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        order = await self.order_repo.create(order, db)

        # 주문 항목 생성
        order_items = [
            OrderItem(
                order_id=order.id,
                menu_id=item["menu_id"],
                menu_name=item["menu_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )
            for item in validated_items
        ]
        await self.order_repo.create_order_items(order_items, db)
        await db.commit()
        await db.refresh(order, attribute_names=["items"])

        # 6. SSE 이벤트 발행 (트랜잭션 커밋 후)
        items_preview = ", ".join(
            f"{item['menu_name']} x{item['quantity']}" for item in validated_items
        )
        await sse_manager.publish_to_store(store_id, {
            "event_type": "new_order",
            "data": {
                "order_id": order.id,
                "order_number": order.order_number,
                "table_id": order.table_id,
                "total_amount": order.total_amount,
                "items_preview": items_preview,
                "status": order.status.value,
                "ordered_at": order.ordered_at.isoformat(),
            },
        })

        logger.info(
            "주문 생성 완료: order_id=%s, order_number=%s, total=%s",
            order.id,
            order.order_number,
            total_amount,
        )
        return order

    # ── 주문 조회 ──

    async def get_table_orders(
        self, table_id: int, session_id: int, db: AsyncSession
    ) -> list[Order]:
        """테이블 현재 세션 주문 조회 (US-CU-10)."""
        return await self.order_repo.get_by_table_and_session(
            table_id, session_id, db
        )

    async def get_store_orders(
        self, store_id: int, db: AsyncSession
    ) -> list[Order]:
        """매장 전체 활성 주문 조회 (US-MA-07)."""
        return await self.order_repo.get_by_store(store_id, db)

    # ── 주문 상태 변경 (US-MA-09) ──

    async def update_order_status(
        self,
        order_id: int,
        new_status_str: str,
        store_id: int,
        db: AsyncSession,
    ) -> Order:
        """주문 상태 변경.

        상태 전이 규칙:
        - PENDING → PREPARING
        - PREPARING → COMPLETED
        - 역방향 전이 불가

        Raises:
            HTTPException: 주문 미존재, 권한 없음, 잘못된 상태 전이
        """
        order = await self.order_repo.get_by_id(order_id, db)
        if order is None:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        if order.store_id != store_id:
            raise HTTPException(status_code=403, detail="해당 매장의 주문이 아닙니다")

        new_status = OrderStatus(new_status_str)
        current_status = order.status

        # 상태 전이 검증
        valid_next = VALID_STATUS_TRANSITIONS.get(current_status, [])
        if new_status not in valid_next:
            raise HTTPException(
                status_code=422,
                detail=f"잘못된 상태 전이: {current_status.value} → {new_status.value}",
            )

        previous_status = current_status.value
        updated_order = await self.order_repo.update_status(order_id, new_status, db)
        await db.commit()

        # SSE 이벤트 발행 (관리자 + 고객)
        event_data = {
            "event_type": "order_status_changed",
            "data": {
                "order_id": order_id,
                "order_number": order.order_number,
                "table_id": order.table_id,
                "previous_status": previous_status,
                "new_status": new_status.value,
            },
        }
        await sse_manager.publish_to_store(store_id, event_data)
        await sse_manager.publish_to_table(order.table_id, event_data)

        logger.info(
            "주문 상태 변경: order_id=%s, %s → %s",
            order_id,
            previous_status,
            new_status.value,
        )
        return updated_order

    # ── 주문 삭제 (US-MA-11) ──

    async def delete_order(
        self, order_id: int, store_id: int, db: AsyncSession
    ) -> None:
        """주문 삭제 (관리자 직권).

        Raises:
            HTTPException: 주문 미존재, 권한 없음
        """
        order = await self.order_repo.get_by_id(order_id, db)
        if order is None:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        if order.store_id != store_id:
            raise HTTPException(status_code=403, detail="해당 매장의 주문이 아닙니다")

        table_id = order.table_id
        order_number = order.order_number

        deleted = await self.order_repo.delete_order(order_id, db)
        if not deleted:
            raise HTTPException(status_code=500, detail="주문 삭제에 실패했습니다")
        await db.commit()

        # SSE 이벤트 발행
        await sse_manager.publish_to_store(store_id, {
            "event_type": "order_deleted",
            "data": {
                "order_id": order_id,
                "table_id": table_id,
                "order_number": order_number,
            },
        })

        logger.info("주문 삭제: order_id=%s, order_number=%s", order_id, order_number)

    # ── 이력 이동 (US-MA-12) ──

    async def move_to_history(
        self, session_id: int, store_id: int, db: AsyncSession
    ) -> int:
        """세션의 모든 주문을 OrderHistory로 이동.

        트랜잭션 내에서 실행:
        1. 세션의 모든 주문 조회
        2. 각 주문 → OrderHistory 생성 (items_json 포함)
        3. 원본 Order + OrderItem 삭제

        Returns:
            이동된 주문 수
        """
        orders = await self.order_repo.get_by_session(session_id, db)
        if not orders:
            return 0

        completed_at = datetime.utcnow()
        moved_count = 0
        table_id = orders[0].table_id if orders else 0

        for order in orders:
            # 주문 항목을 JSON으로 직렬화
            items = await self.order_repo.get_order_items(order.id, db)
            items_json = [item.to_dict() for item in items]

            # OrderHistory 생성
            history = OrderHistory(
                original_order_id=order.id,
                order_number=order.order_number,
                store_id=order.store_id,
                table_id=order.table_id,
                session_id=order.session_id,
                status=order.status.value if order.status else "UNKNOWN",
                payment_type=order.payment_type.value if order.payment_type else "UNKNOWN",
                total_amount=order.total_amount,
                items_json=items_json,
                ordered_at=order.ordered_at,
                completed_at=completed_at,
            )
            await self.order_repo.create_history(history, db)

            # 원본 삭제
            await self.order_repo.delete_order_items(order.id, db)
            await self.order_repo.delete_order(order.id, db)
            moved_count += 1

        await db.commit()

        # SSE 이벤트 발행
        await sse_manager.publish_to_store(store_id, {
            "event_type": "table_completed",
            "data": {
                "table_id": table_id,
                "completed_orders_count": moved_count,
            },
        })

        logger.info(
            "이력 이동 완료: session_id=%s, moved=%s orders",
            session_id,
            moved_count,
        )
        return moved_count

    # ── 과거 주문 이력 조회 (US-MA-13) ──

    async def get_order_history(
        self,
        table_id: int,
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[OrderHistory]:
        """테이블별 과거 주문 이력 조회."""
        return await self.order_repo.get_history_by_table(
            table_id, db, date_from=date_from, date_to=date_to
        )

    # ── 테이블 총 주문액 ──

    async def get_table_total(
        self, table_id: int, session_id: int, db: AsyncSession
    ) -> int:
        """테이블 현재 세션 총 주문액 계산."""
        return await self.order_repo.get_table_total(table_id, session_id, db)
