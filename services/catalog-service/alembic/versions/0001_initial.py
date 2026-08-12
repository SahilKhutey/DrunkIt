"""Initial schema for catalog service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "brands",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("manufacturer", sa.String(128), nullable=False),
        sa.Column("origin_country", sa.String(2), nullable=False, server_default="IN"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "product_masters",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gtin", sa.String(14), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("brand_id", sa.String(36), sa.ForeignKey("brands.id"), nullable=False, index=True),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=False, index=True),
        sa.Column("volume_ml", sa.Integer(), nullable=False),
        sa.Column("abv_percentage", sa.Float(), nullable=False),
        sa.Column("packaging_type", sa.String(32), nullable=False, server_default="GLASS_BOTTLE"),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "skus",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("product_masters.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sku_code", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("barcode", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("pack_size", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("state_excise_code", sa.String(64), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "store_listings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_id", sa.String(36), nullable=False, index=True),
        sa.Column("sku_id", sa.String(36), sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("mrp_inr", sa.Float(), nullable=False),
        sa.Column("selling_price_inr", sa.Float(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("store_listings")
    op.drop_table("skus")
    op.drop_table("product_masters")
    op.drop_table("brands")
    op.drop_table("categories")
