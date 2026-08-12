"""Initial schema for inventory service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("sku_id", sa.String(36), nullable=False, index=True),
        sa.Column("available_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_level", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("uix_store_sku_inventory", "inventory_items", ["store_id", "sku_id"], unique=True)

    op.create_table(
        "inventory_reservations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("reservation_token", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("sku_id", sa.String(36), nullable=False, index=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="HELD", index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "inventory_audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("sku_id", sa.String(36), nullable=False, index=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("quantity_change", sa.Integer(), nullable=False),
        sa.Column("resulting_balance", sa.Integer(), nullable=False),
        sa.Column("performed_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("inventory_audit_logs")
    op.drop_table("inventory_reservations")
    op.drop_table("inventory_items")
