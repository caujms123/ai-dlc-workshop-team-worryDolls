"""Unit 3: Order, OrderItem, OrderHistory 테이블 생성

Revision ID: 003
Revises: 002
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Order 테이블 ──
    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("order_number", sa.String(20), nullable=False),
        sa.Column("store_id", sa.BigInteger(), nullable=False),
        sa.Column("table_id", sa.BigInteger(), nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PREPARING", "COMPLETED", name="orderstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "payment_type",
            sa.Enum("DUTCH_PAY", "SINGLE_PAY", name="paymenttype"),
            nullable=False,
        ),
        sa.Column("total_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ordered_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.ForeignKeyConstraint(["table_id"], ["table_info.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["table_sessions.id"]),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)
    op.create_index("ix_orders_store_status", "orders", ["store_id", "status"])
    op.create_index("ix_orders_table_session", "orders", ["table_id", "session_id"])

    # ── OrderItem 테이블 ──
    op.create_table(
        "order_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("menu_id", sa.BigInteger(), nullable=False),
        sa.Column("menu_name", sa.String(100), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["menu_id"], ["menus.id"]),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
    )

    # ── OrderHistory 테이블 ──
    op.create_table(
        "order_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("original_order_id", sa.BigInteger(), nullable=False),
        sa.Column("order_number", sa.String(20), nullable=False),
        sa.Column("store_id", sa.BigInteger(), nullable=False),
        sa.Column("table_id", sa.BigInteger(), nullable=False),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("payment_type", sa.String(20), nullable=False),
        sa.Column("total_amount", sa.Integer(), nullable=False),
        sa.Column("items_json", sa.JSON(), nullable=False),
        sa.Column("ordered_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
    )
    op.create_index(
        "ix_order_history_store_table_completed",
        "order_history",
        ["store_id", "table_id", "completed_at"],
    )


def downgrade() -> None:
    op.drop_table("order_history")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS paymenttype")
