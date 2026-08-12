"""Initial schema for payment service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_intents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), nullable=False, index=True),
        sa.Column("consumer_id", sa.String(36), nullable=False, index=True),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(32), nullable=False, server_default="CREATED", index=True),
        sa.Column("gateway_provider", sa.String(32), nullable=False, server_default="STUB_PAY"),
        sa.Column("gateway_transaction_id", sa.String(64), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "payment_transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("intent_id", sa.String(36), sa.ForeignKey("payment_intents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("transaction_type", sa.String(32), nullable=False),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "double_entry_ledgers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entry_id", sa.String(64), nullable=False, index=True),
        sa.Column("account_debit", sa.String(64), nullable=False, index=True),
        sa.Column("account_credit", sa.String(64), nullable=False, index=True),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.Column("reference_id", sa.String(64), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("double_entry_ledgers")
    op.drop_table("payment_transactions")
    op.drop_table("payment_intents")
