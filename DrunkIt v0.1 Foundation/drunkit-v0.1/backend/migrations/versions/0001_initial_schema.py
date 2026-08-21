"""0001 Initial Schema for DrunkIt v0.1

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-21 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users & Roles
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("email", sa.Text(), nullable=True, unique=True),
        sa.Column("phone", sa.Text(), nullable=True, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.UUID(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "consumer_profiles",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferred_market", sa.Text(), nullable=True),
        sa.Column("date_of_birth_verified", sa.Boolean(), nullable=False, server_default="false"),
    )

    # 2. Master Catalog
    op.create_table(
        "brands",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("parent_id", sa.UUID(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("brand_id", sa.UUID(), sa.ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.UUID(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("product_type", sa.String(100), nullable=False),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("country_of_origin", sa.String(2), nullable=True),
        sa.Column("abv", sa.Numeric(5, 2), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_products_brand", "products", ["brand_id"])
    op.create_index("idx_products_category", "products", ["category_id"])

    op.create_table(
        "product_variants",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("volume_ml", sa.Integer(), nullable=False),
        sa.Column("packaging_type", sa.String(50), nullable=True),
        sa.Column("package_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.CheckConstraint("volume_ml > 0", name="chk_variant_volume_positive"),
        sa.CheckConstraint("package_count > 0", name="chk_variant_package_count_positive"),
        sa.UniqueConstraint("product_id", "volume_ml", "packaging_type", "package_count", name="uq_product_variant_specs"),
    )
    op.create_table(
        "skus",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("variant_id", sa.UUID(), sa.ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("canonical_code", sa.String(100), nullable=False, unique=True),
        sa.Column("barcode", sa.String(100), nullable=True, unique=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
    )
    op.create_table(
        "product_attributes",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
    )
    op.create_index("idx_product_attributes_key_value", "product_attributes", ["key", "value"])

    op.create_table(
        "taste_profiles",
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("body", sa.Numeric(5, 4), nullable=True),
        sa.Column("sweetness", sa.Numeric(5, 4), nullable=True),
        sa.Column("smokiness", sa.Numeric(5, 4), nullable=True),
        sa.Column("bitterness", sa.Numeric(5, 4), nullable=True),
        sa.Column("fruitiness", sa.Numeric(5, 4), nullable=True),
        sa.Column("spiciness", sa.Numeric(5, 4), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
    )

    # 3. Retailers & Locations
    op.create_table(
        "retailers",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("licence_status", sa.String(50), nullable=False, server_default="UNKNOWN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "retailer_locations",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("retailer_id", sa.UUID(), sa.ForeignKey("retailers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state_code", sa.String(10), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=False, server_default="IN"),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
    )
    op.create_index("idx_retailer_locations_geo", "retailer_locations", ["country_code", "state_code", "city"])

    op.create_table(
        "jurisdictions",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("state_code", sa.String(10), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.UniqueConstraint("country_code", "state_code", name="uq_jurisdiction_country_state"),
    )
    op.create_table(
        "retailer_licences",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("retailer_id", sa.UUID(), sa.ForeignKey("retailers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jurisdiction_id", sa.UUID(), sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("licence_number", sa.String(100), nullable=False),
        sa.Column("licence_type", sa.String(50), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("evidence_uri", sa.Text(), nullable=True),
    )

    # 4. Inventory & Pricing
    op.create_table(
        "retailer_skus",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("retailer_location_id", sa.UUID(), sa.ForeignKey("retailer_locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.UUID(), sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("external_sku", sa.String(100), nullable=True),
        sa.Column("external_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.UniqueConstraint("retailer_location_id", "sku_id", name="uq_location_sku"),
    )
    op.create_table(
        "inventory_snapshots",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("retailer_sku_id", sa.UUID(), sa.ForeignKey("retailer_skus.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("availability_status", sa.String(50), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=True),
        sa.CheckConstraint("quantity >= 0", name="chk_inventory_quantity_non_negative"),
    )
    op.create_index("idx_inventory_freshness", "inventory_snapshots", ["retailer_sku_id", "captured_at"])

    op.create_table(
        "prices",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("retailer_sku_id", sa.UUID(), sa.ForeignKey("retailer_skus.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount_minor", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount_minor >= 0", name="chk_price_amount_non_negative"),
    )
    op.create_index("idx_prices_active", "prices", ["retailer_sku_id", "effective_from", "effective_to"])

    # 5. Regulatory & Compliance
    op.create_table(
        "compliance_rule_sets",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("jurisdiction_id", sa.UUID(), sa.ForeignKey("jurisdictions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("source_reference", sa.Text(), nullable=False),
        sa.UniqueConstraint("jurisdiction_id", "version", name="uq_jurisdiction_ruleset_version"),
    )
    op.create_table(
        "compliance_rules",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("rule_set_id", sa.UUID(), sa.ForeignKey("compliance_rule_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("product_class", sa.String(50), nullable=True),
        sa.Column("licence_type", sa.String(50), nullable=True),
        sa.Column("age_requirement", sa.Integer(), nullable=True),
        sa.Column("ordering_allowed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("delivery_allowed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("payment_allowed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("conditions_json", sa.JSON(), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=False),
    )
    op.create_table(
        "compliance_checks",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("correlation_id", sa.UUID(), nullable=False),
        sa.Column("consumer_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("jurisdiction_id", sa.UUID(), sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("retailer_id", sa.UUID(), sa.ForeignKey("retailers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("context_json", sa.JSON(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "compliance_decisions",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("compliance_check_id", sa.UUID(), sa.ForeignKey("compliance_checks.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason_codes", sa.JSON(), nullable=False),
        sa.Column("required_checks", sa.JSON(), nullable=False),
        sa.Column("rule_set_version", sa.String(50), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # 6. Commerce & Cart
    op.create_table(
        "carts",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("consumer_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jurisdiction_id", sa.UUID(), sa.ForeignKey("jurisdictions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "cart_items",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("cart_id", sa.UUID(), sa.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.UUID(), sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("retailer_location_id", sa.UUID(), sa.ForeignKey("retailer_locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price_snapshot", sa.JSON(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_cart_item_quantity_positive"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("consumer_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("retailer_location_id", sa.UUID(), sa.ForeignKey("retailer_locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("subtotal_minor", sa.BigInteger(), nullable=False),
        sa.Column("total_minor", sa.BigInteger(), nullable=False),
        sa.Column("compliance_decision_id", sa.UUID(), sa.ForeignKey("compliance_decisions.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("subtotal_minor >= 0", name="chk_order_subtotal_non_negative"),
        sa.CheckConstraint("total_minor >= 0", name="chk_order_total_non_negative"),
        sa.UniqueConstraint("consumer_id", "idempotency_key", name="uq_consumer_order_idempotency"),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("order_id", sa.UUID(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.UUID(), sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_minor", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_order_item_quantity_positive"),
        sa.CheckConstraint("unit_price_minor >= 0", name="chk_order_item_price_non_negative"),
    )

    # 7. Audit & Outbox
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("actor_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("aggregate_type", sa.String(100), nullable=True),
        sa.Column("aggregate_id", sa.UUID(), nullable=True),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column("causation_id", sa.UUID(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("audit_logs")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("compliance_decisions")
    op.drop_table("compliance_checks")
    op.drop_table("compliance_rules")
    op.drop_table("compliance_rule_sets")
    op.drop_table("prices")
    op.drop_table("inventory_snapshots")
    op.drop_table("retailer_skus")
    op.drop_table("retailer_licences")
    op.drop_table("jurisdictions")
    op.drop_table("retailer_locations")
    op.drop_table("retailers")
    op.drop_table("taste_profiles")
    op.drop_table("product_attributes")
    op.drop_table("skus")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("brands")
    op.drop_table("consumer_profiles")
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("users")
