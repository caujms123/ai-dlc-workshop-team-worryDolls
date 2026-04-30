"""테이블 및 세션 도메인 모델 (Unit 4)"""

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class TableInfo(Base):
    """테이블 정보"""
    __tablename__ = "table_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(BigInteger, ForeignKey("store.id"), nullable=False)
    table_number = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("TableSession", back_populates="table", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("store_id", "table_number", name="uq_store_table_number"),
    )


class TableSession(Base):
    """테이블 세션 (고객 이용 단위)"""
    __tablename__ = "table_session"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    table_id = Column(BigInteger, ForeignKey("table_info.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("store.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    table = relationship("TableInfo", back_populates="sessions")

    __table_args__ = (
        Index("ix_table_session_active", "table_id", "is_active"),
    )
