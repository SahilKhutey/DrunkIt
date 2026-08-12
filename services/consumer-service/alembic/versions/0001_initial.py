"""Initial schema for consumer service."""

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
        "consumer_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("consumer_level", sa.String(32), nullable=False, server_default="C1_REGISTERED", index=True),
        sa.Column("is_age_verified", sa.Boolean(), nullable=False, server_default="false", index=True),
        sa.Column("age_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("kyc_status", sa.String(32), nullable=False, server_default="NOT_STARTED"),
        sa.Column("primary_jurisdiction", sa.String(64), nullable=False, server_default="IN-KA", index=True),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("trust_score", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "delivery_addresses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("consumer_id", sa.String(36), sa.ForeignKey("consumer_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("label", sa.String(32), nullable=False, server_default="Home"),
        sa.Column("recipient_name", sa.String(128), nullable=False),
        sa.Column("recipient_phone", sa.String(32), nullable=False),
        sa.Column("address_line_1", sa.String(255), nullable=False),
        sa.Column("address_line_2", sa.String(255), nullable=True),
        sa.Column("landmark", sa.String(128), nullable=True),
        sa.Column("city", sa.String(64), nullable=False, index=True),
        sa.Column("state", sa.String(64), nullable=False, index=True),
        sa.Column("pincode", sa.String(16), nullable=False, index=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("delivery_instructions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "age_verification_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("consumer_id", sa.String(36), sa.ForeignKey("consumer_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("verification_type", sa.String(32), nullable=False),
        sa.Column("document_type", sa.String(32), nullable=False),
        sa.Column("document_hash", sa.String(128), nullable=False),
        sa.Column("verified_age", sa.Integer(), nullable=False),
        sa.Column("verification_status", sa.String(32), nullable=False, index=True),
        sa.Column("verifier_provider", sa.String(64), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("details", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "consumer_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("consumer_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("favorite_categories", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("allow_promotions", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("preferred_payment_method", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("consumer_preferences")
    op.drop_table("age_verification_records")
    op.drop_table("delivery_addresses")
    op.drop_table("consumer_profiles")
