"""Initial schema for whitelabel service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_branding_configs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("brand_name", sa.String(128), nullable=False),
        sa.Column("logo_url", sa.String(255), nullable=True),
        sa.Column("primary_color_hex", sa.String(7), nullable=False, server_default="#1a202c"),
        sa.Column("secondary_color_hex", sa.String(7), nullable=False, server_default="#319795"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "custom_domain_bindings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("domain_name", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("ssl_certified", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("custom_domain_bindings")
    op.drop_table("tenant_branding_configs")
