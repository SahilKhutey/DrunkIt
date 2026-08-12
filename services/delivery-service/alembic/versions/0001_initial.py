"""Initial schema for delivery service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "delivery_missions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mission_code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("order_id", sa.String(36), nullable=False, index=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("consumer_id", sa.String(36), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="QUEUED", index=True),
        sa.Column("delivery_otp_hash", sa.String(64), nullable=False),
        sa.Column("pickup_address", sa.String(255), nullable=False),
        sa.Column("dropoff_address", sa.String(255), nullable=False),
        sa.Column("assigned_driver_id", sa.String(36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "delivery_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mission_id", sa.String(36), sa.ForeignKey("delivery_missions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("driver_id", sa.String(36), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACCEPTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "delivery_location_pings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mission_id", sa.String(36), sa.ForeignKey("delivery_missions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("driver_id", sa.String(36), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "proof_of_deliveries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mission_id", sa.String(36), sa.ForeignKey("delivery_missions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("recipient_verified", sa.Boolean(), nullable=False),
        sa.Column("verification_method", sa.String(32), nullable=False, server_default="OTP_SMS"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("proof_of_deliveries")
    op.drop_table("delivery_location_pings")
    op.drop_table("delivery_assignments")
    op.drop_table("delivery_missions")
