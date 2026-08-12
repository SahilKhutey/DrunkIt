"""Initial schema for compliance service."""

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
        "policies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("category", sa.String(64), nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("min_purchasing_age", sa.Integer(), nullable=False, server_default="21"),
        sa.Column("max_volume_per_transaction_ml", sa.Integer(), nullable=True),
        sa.Column("max_volume_per_day_ml", sa.Integer(), nullable=True),
        sa.Column("sales_start_time", sa.Time(), nullable=False, server_default="10:00:00"),
        sa.Column("sales_end_time", sa.Time(), nullable=False, server_default="22:00:00"),
        sa.Column("metadata_json", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "jurisdiction_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("policy_id", sa.String(36), sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("rule_code", sa.String(64), nullable=False, index=True),
        sa.Column("rule_type", sa.String(64), nullable=False, index=True),
        sa.Column("parameters", JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "dry_day_calendars",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("dry_date", sa.Date(), nullable=False, index=True),
        sa.Column("occasion", sa.String(128), nullable=False),
        sa.Column("is_full_day", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_dry_days_jur_date", "dry_day_calendars", ["jurisdiction", "dry_date"], unique=True)

    op.create_table(
        "license_requirements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("license_type", sa.String(64), nullable=False, index=True),
        sa.Column("issuing_authority", sa.String(128), nullable=False),
        sa.Column("validity_months", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("requires_renewal_notice_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "compliance_checks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("reference_id", sa.String(64), nullable=False, index=True),
        sa.Column("check_type", sa.String(64), nullable=False, index=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, index=True),
        sa.Column("actor_id", sa.String(36), nullable=False, index=True),
        sa.Column("is_compliant", sa.Boolean(), nullable=False, index=True),
        sa.Column("failure_reasons", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("details", JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("compliance_checks")
    op.drop_table("license_requirements")
    op.drop_table("dry_day_calendars")
    op.drop_table("jurisdiction_rules")
    op.drop_table("policies")
