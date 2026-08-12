"""Initial schema for risk service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("evaluation_code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("entity_type", sa.String(32), nullable=False, index=True),
        sa.Column("entity_id", sa.String(64), nullable=False, index=True),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False, index=True),
        sa.Column("reason_codes_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "fraud_pattern_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rule_name", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("risk_score_impact", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("fraud_pattern_rules")
    op.drop_table("risk_evaluations")
