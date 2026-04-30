"""Order, OrderItem, OrderHistory SQLAlchemy 모델 정의."""

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    """주문 상태 열거형."""

    PENDING = "PENDING"
    PREPARING = "PREPARING"
    COMPLETED = "COMPLETED"


class PaymentType(str, enum.Enum):
    """결제 방식 열거형."""

    DUTCH_PAY = "DUTCH_PAY"
    SINGLE_PAY = "SINGLE_PAY"


# 유효한 상태 전이 맵
VALID_STATUS_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.PENDING: [OrderStatus.PREPARING],
    OrderStatus.PREPARING: [OrderStatus.COMPLETED],
    OrderStatus.COMPLETED: [],
}


class Order(Base):
    """주문 테이블."""

    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_number = Column(String(20), unique=True, nullable=False, index=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    table_id = Column(BigInteger, ForeignKey("table_info.id"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("table_sessions.id"), nullable=False)
    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    payment_type = Column(Enum(PaymentType), nullable=False)
    total_amount = Column(Integer, nullable=False, default=0)
    ordered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_orders_store_status", "store_id", "status"),
        Index("ix_orders_table_session", "table_id", "session_id"),
    )

    def to_dict(self) -> dict:
        """Order를 딕셔너리로 변환."""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "store_id": self.store_id,
            "table_id": self.table_id,
            "session_id": self.session_id,
            "status": self.status.value if self.status else None,
            "payment_type": self.payment_type.value if self.payment_type else None,
            "total_amount": self.total_amount,
            "ordered_at": self.ordered_at.isoformat() if self.ordered_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItem(Base):
    """주문 항목 테이블."""

    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    menu_id = Column(BigInteger, ForeignKey("menus.id"), nullable=False)
    menu_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
    )

    def to_dict(self) -> dict:
        """OrderItem을 딕셔너리로 변환."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "menu_id": self.menu_id,
            "menu_name": self.menu_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.subtotal,
        }


class OrderHistory(Base):
    """과거 주문 이력 테이블."""

    __tablename__ = "order_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    original_order_id = Column(BigInteger, nullable=False)
    order_number = Column(String(20), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    table_id = Column(BigInteger, nullable=False)
    session_id = Column(BigInteger, nullable=False)
    status = Column(String(20), nullable=False)
    payment_type = Column(String(20), nullable=False)
    total_amount = Column(Integer, nullable=False)
    items_json = Column(JSON, nullable=False)
    ordered_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_order_history_store_table_completed", "store_id", "table_id", "completed_at"),
    )

    def to_dict(self) -> dict:
        """OrderHistory를 딕셔너리로 변환."""
        return {
            "id": self.id,
            "original_order_id": self.original_order_id,
            "order_number": self.order_number,
            "store_id": self.store_id,
            "table_id": self.table_id,
            "session_id": self.session_id,
            "status": self.status,
            "payment_type": self.payment_type,
            "total_amount": self.total_amount,
            "items_json": self.items_json,
            "ordered_at": self.ordered_at.isoformat() if self.ordered_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
