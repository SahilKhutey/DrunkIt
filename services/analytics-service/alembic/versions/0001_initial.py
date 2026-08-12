"""Initial schema for analytics service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metric_aggregates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("metric_name", sa.String(64), nullable=False, index=True),
        sa.Column("dimension_key", sa.String(64), nullable=False, index=True),
        sa.Column("dimension_value", sa.String(64), nullable=False, index=True),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "report_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("snapshot_code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("report_type", sa.String(64), nullable=False, index=True),
        sa.Column("generated_by", sa.String(64), nullable=False),
        sa.Column("snapshot_data_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("report_snapshots")
    op.drop_table("metric_aggregates")
