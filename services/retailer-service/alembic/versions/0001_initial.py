"""Initial schema for retailer service."""

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
        "retailer_organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("legal_name", sa.String(128), nullable=False),
        sa.Column("trade_name", sa.String(128), nullable=False, index=True),
        sa.Column("business_type", sa.String(64), nullable=False),
        sa.Column("gstin", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("pan", sa.String(16), unique=True, nullable=False, index=True),
        sa.Column("owner_user_id", sa.String(36), nullable=False, index=True),
        sa.Column("seller_level", sa.String(32), nullable=False, server_default="S1_BASIC", index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "stores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("retailer_organizations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("store_type", sa.String(32), nullable=False, server_default="CL_2"),
        sa.Column("address_line_1", sa.String(255), nullable=False),
        sa.Column("address_line_2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(64), nullable=False, index=True),
        sa.Column("state", sa.String(64), nullable=False, index=True),
        sa.Column("pincode", sa.String(16), nullable=False, index=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("is_accepting_orders", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "store_licenses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("license_number", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("license_type", sa.String(32), nullable=False, index=True),
        sa.Column("issuing_authority", sa.String(128), nullable=False),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE", index=True),
        sa.Column("document_url", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "store_operating_hours",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=False),
        sa.Column("close_time", sa.Time(), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "store_staff_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("role_in_store", sa.String(32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("store_staff_assignments")
    op.drop_table("store_operating_hours")
    op.drop_table("store_licenses")
    op.drop_table("stores")
    op.drop_table("retailer_organizations")
