"""Initial schema for order service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_number", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("consumer_id", sa.String(36), nullable=False, index=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("delivery_address_id", sa.String(36), nullable=False),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("order_state", sa.String(32), nullable=False, server_default="DRAFT", index=True),
        sa.Column("total_amount_inr", sa.Float(), nullable=False),
        sa.Column("delivery_fee_inr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("excise_tax_inr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("reservation_token", sa.String(64), nullable=True, index=True),
        sa.Column("payment_intent_id", sa.String(64), nullable=True, index=True),
        sa.Column("cancellation_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sku_id", sa.String(36), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("unit_price_inr", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal_inr", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "order_state_histories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_state", sa.String(32), nullable=False),
        sa.Column("to_state", sa.String(32), nullable=False),
        sa.Column("triggered_by", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "compliance_validation_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("is_compliant", sa.Boolean(), nullable=False),
        sa.Column("evaluation_id", sa.String(64), nullable=False),
        sa.Column("rules_checked", JSONB(), nullable=False, server_default="{}"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("compliance_validation_records")
    op.drop_table("order_state_histories")
    op.drop_table("order_items")
    op.drop_table("orders")
