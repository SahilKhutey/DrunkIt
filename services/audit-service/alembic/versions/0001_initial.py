"""Initial schema for audit service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cryptographic_audit_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sequence_number", sa.Integer(), autoincrement=True, unique=True, nullable=False, index=True),
        sa.Column("event_id", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("event_type", sa.String(128), nullable=False, index=True),
        sa.Column("actor_id", sa.String(64), nullable=False, index=True),
        sa.Column("actor_role", sa.String(32), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False, index=True),
        sa.Column("resource_id", sa.String(64), nullable=False, index=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=False),
        sa.Column("current_hash", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("cryptographic_audit_entries")
