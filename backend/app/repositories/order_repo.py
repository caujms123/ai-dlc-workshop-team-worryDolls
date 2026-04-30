"""주문 Repository - 데이터 접근 계층."""

import logging
from datetime import date, datetime
from typing import Optional

from sqlalchemy import delete, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderHistory, OrderStatus

logger = logging.getLogger(__name__)


class OrderRepository:
    """Order 데이터 접근 객체."""

    # ── Order CRUD ──

    async def create(self, order: Order, db: AsyncSession) -> Order:
        """주문 생성."""
        db.add(order)
        await db.flush()
        await db.refresh(order, attribute_names=["items"])
        logger.info("주문 생성: order_id=%s, order_number=%s", order.id, order.order_number)
        return order

    async def get_by_id(
        self, order_id: int, db: AsyncSession, *, with_items: bool = True
    ) -> Optional[Order]:
        """주문 ID로 조회."""
        stmt = select(Order).where(Order.id == order_id)
        if with_items:
            stmt = stmt.options(selectinload(Order.items))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_session(
        self, session_id: int, db: AsyncSession
    ) -> list[Order]:
        """세션별 주문 목록 조회 (최신순)."""
        stmt = (
            select(Order)
            .where(Order.session_id == session_id)
            .options(selectinload(Order.items))
            .order_by(Order.ordered_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_store(
        self, store_id: int, db: AsyncSession
    ) -> list[Order]:
        """매장별 활성 주문 목록 조회."""
        stmt = (
            select(Order)
            .where(Order.store_id == store_id)
            .options(selectinload(Order.items))
            .order_by(Order.ordered_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_table_and_session(
        self, table_id: int, session_id: int, db: AsyncSession
    ) -> list[Order]:
        """테이블+세션별 주문 목록 조회 (최신순)."""
        stmt = (
            select(Order)
            .where(
                and_(Order.table_id == table_id, Order.session_id == session_id)
            )
            .options(selectinload(Order.items))
            .order_by(Order.ordered_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, order_id: int, status: OrderStatus, db: AsyncSession
    ) -> Optional[Order]:
        """주문 상태 업데이트."""
        order = await self.get_by_id(order_id, db, with_items=True)
        if order is None:
            return None
        order.status = status
        order.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(order)
        logger.info(
            "주문 상태 변경: order_id=%s, new_status=%s", order_id, status.value
        )
        return order

    async def delete_order(self, order_id: int, db: AsyncSession) -> bool:
        """주문 삭제 (CASCADE로 OrderItem도 삭제)."""
        order = await self.get_by_id(order_id, db, with_items=False)
        if order is None:
            return False
        await db.delete(order)
        await db.flush()
        logger.info("주문 삭제: order_id=%s", order_id)
        return True

    async def count_today_orders(
        self, store_id: int, today_str: str, db: AsyncSession
    ) -> int:
        """해당 매장의 오늘 주문 수 조회 (주문 번호 생성용)."""
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.store_id == store_id,
                Order.order_number.like(f"ORD-{today_str}-%"),
            )
        )
        result = await db.execute(stmt)
        return result.scalar() or 0

    # ── OrderItem ──

    async def create_order_items(
        self, items: list[OrderItem], db: AsyncSession
    ) -> list[OrderItem]:
        """주문 항목 일괄 생성."""
        db.add_all(items)
        await db.flush()
        return items

    async def get_order_items(
        self, order_id: int, db: AsyncSession
    ) -> list[OrderItem]:
        """주문 항목 조회."""
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete_order_items(
        self, order_id: int, db: AsyncSession
    ) -> None:
        """주문 항목 일괄 삭제."""
        stmt = delete(OrderItem).where(OrderItem.order_id == order_id)
        await db.execute(stmt)

    # ── OrderHistory ──

    async def create_history(
        self, history: OrderHistory, db: AsyncSession
    ) -> OrderHistory:
        """주문 이력 생성."""
        db.add(history)
        await db.flush()
        logger.info(
            "주문 이력 생성: original_order_id=%s", history.original_order_id
        )
        return history

    async def get_history_by_table(
        self,
        table_id: int,
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[OrderHistory]:
        """테이블별 과거 주문 이력 조회 (시간 역순)."""
        stmt = select(OrderHistory).where(OrderHistory.table_id == table_id)
        if date_from:
            stmt = stmt.where(
                OrderHistory.completed_at >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            stmt = stmt.where(
                OrderHistory.completed_at <= datetime.combine(date_to, datetime.max.time())
            )
        stmt = stmt.order_by(OrderHistory.completed_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_history_by_store(
        self,
        store_id: int,
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[OrderHistory]:
        """매장별 과거 주문 이력 조회 (시간 역순)."""
        stmt = select(OrderHistory).where(OrderHistory.store_id == store_id)
        if date_from:
            stmt = stmt.where(
                OrderHistory.completed_at >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            stmt = stmt.where(
                OrderHistory.completed_at <= datetime.combine(date_to, datetime.max.time())
            )
        stmt = stmt.order_by(OrderHistory.completed_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_table_total(
        self, table_id: int, session_id: int, db: AsyncSession
    ) -> int:
        """테이블 현재 세션 총 주문액 계산."""
        stmt = select(func.coalesce(func.sum(Order.total_amount), 0)).where(
            and_(Order.table_id == table_id, Order.session_id == session_id)
        )
        result = await db.execute(stmt)
        return result.scalar() or 0
