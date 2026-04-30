"""Category database model."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    """Category entity representing a menu category within a store."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationships
    menus = relationship("Menu", back_populates="category", lazy="selectin")

    __table_args__ = (
        Index("ix_categories_store_order", "store_id", "display_order"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', store_id={self.store_id})>"
