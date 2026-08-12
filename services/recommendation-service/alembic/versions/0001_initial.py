"""Initial schema for recommendation service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consumer_preference_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("consumer_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("preferred_categories_json", sa.Text(), nullable=False),
        sa.Column("preferred_brands_json", sa.Text(), nullable=False),
        sa.Column("price_sensitivity_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "product_affinity_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sku_id_a", sa.String(36), nullable=False, index=True),
        sa.Column("sku_id_b", sa.String(36), nullable=False, index=True),
        sa.Column("affinity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("product_affinity_scores")
    op.drop_table("consumer_preference_profiles")
