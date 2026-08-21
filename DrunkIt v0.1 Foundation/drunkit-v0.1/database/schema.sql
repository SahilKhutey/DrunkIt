-- DrunkIt v0.1 initial PostgreSQL schema
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    password_hash TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE consumer_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    preferred_market TEXT,
    date_of_birth_verified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    country_code CHAR(2),
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(id),
    category_id UUID REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    product_type TEXT NOT NULL,
    region TEXT,
    country_of_origin CHAR(2),
    abv NUMERIC(5,2),
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('simple', name));

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    volume_ml INTEGER NOT NULL CHECK (volume_ml > 0),
    packaging_type TEXT,
    package_count INTEGER NOT NULL DEFAULT 1 CHECK (package_count > 0),
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    UNIQUE(product_id, volume_ml, packaging_type, package_count)
);

CREATE TABLE skus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID NOT NULL REFERENCES product_variants(id) ON DELETE CASCADE,
    canonical_code TEXT UNIQUE NOT NULL,
    barcode TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE product_attributes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE INDEX idx_product_attributes_key_value
    ON product_attributes(key, value);

CREATE TABLE taste_profiles (
    product_id UUID PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    body NUMERIC(5,4),
    sweetness NUMERIC(5,4),
    smokiness NUMERIC(5,4),
    bitterness NUMERIC(5,4),
    fruitiness NUMERIC(5,4),
    spiciness NUMERIC(5,4),
    confidence NUMERIC(5,4)
);

CREATE TABLE retailers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    licence_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE retailer_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state_code TEXT NOT NULL,
    postal_code TEXT,
    country_code CHAR(2) NOT NULL,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE INDEX idx_retailer_locations_geo
    ON retailer_locations(country_code, state_code, city);

CREATE TABLE jurisdictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_code CHAR(2) NOT NULL,
    state_code TEXT,
    name TEXT NOT NULL,
    timezone TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    UNIQUE(country_code, state_code)
);

CREATE TABLE retailer_licences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
    jurisdiction_id UUID NOT NULL REFERENCES jurisdictions(id),
    licence_number TEXT NOT NULL,
    licence_type TEXT NOT NULL,
    valid_from DATE,
    valid_to DATE,
    status TEXT NOT NULL DEFAULT 'PENDING',
    evidence_uri TEXT
);

CREATE TABLE retailer_skus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_location_id UUID NOT NULL REFERENCES retailer_locations(id) ON DELETE CASCADE,
    sku_id UUID NOT NULL REFERENCES skus(id),
    external_sku TEXT,
    external_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    UNIQUE(retailer_location_id, sku_id)
);

CREATE TABLE inventory_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_sku_id UUID NOT NULL REFERENCES retailer_skus(id) ON DELETE CASCADE,
    quantity INTEGER CHECK (quantity >= 0),
    availability_status TEXT NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source TEXT NOT NULL,
    source_reference TEXT
);

CREATE INDEX idx_inventory_freshness
    ON inventory_snapshots(retailer_sku_id, captured_at DESC);

CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_sku_id UUID NOT NULL REFERENCES retailer_skus(id) ON DELETE CASCADE,
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    currency CHAR(3) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_prices_active
    ON prices(retailer_sku_id, effective_from, effective_to);

CREATE TABLE compliance_rule_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jurisdiction_id UUID NOT NULL REFERENCES jurisdictions(id),
    version TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    source_reference TEXT NOT NULL,
    UNIQUE(jurisdiction_id, version)
);

CREATE TABLE compliance_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_set_id UUID NOT NULL REFERENCES compliance_rule_sets(id) ON DELETE CASCADE,
    rule_type TEXT NOT NULL,
    product_class TEXT,
    licence_type TEXT,
    age_requirement INTEGER,
    ordering_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    delivery_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    payment_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    conditions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_reference TEXT NOT NULL
);

CREATE TABLE compliance_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id UUID NOT NULL,
    consumer_id UUID REFERENCES users(id),
    jurisdiction_id UUID NOT NULL REFERENCES jurisdictions(id),
    product_id UUID REFERENCES products(id),
    retailer_id UUID REFERENCES retailers(id),
    context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE compliance_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compliance_check_id UUID NOT NULL REFERENCES compliance_checks(id),
    decision TEXT NOT NULL CHECK (decision IN ('ALLOW', 'DENY', 'REVIEW')),
    reason_codes JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_checks JSONB NOT NULL DEFAULT '[]'::jsonb,
    rule_set_version TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID NOT NULL REFERENCES users(id),
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    sku_id UUID NOT NULL REFERENCES skus(id),
    retailer_location_id UUID NOT NULL REFERENCES retailer_locations(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_snapshot JSONB NOT NULL
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID NOT NULL REFERENCES users(id),
    retailer_location_id UUID NOT NULL REFERENCES retailer_locations(id),
    status TEXT NOT NULL DEFAULT 'PENDING',
    currency CHAR(3) NOT NULL,
    subtotal_minor BIGINT NOT NULL CHECK (subtotal_minor >= 0),
    total_minor BIGINT NOT NULL CHECK (total_minor >= 0),
    compliance_decision_id UUID REFERENCES compliance_decisions(id),
    idempotency_key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(consumer_id, idempotency_key)
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    sku_id UUID NOT NULL REFERENCES skus(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_minor BIGINT NOT NULL CHECK (unit_price_minor >= 0)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    correlation_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 1,
    aggregate_type TEXT,
    aggregate_id UUID,
    correlation_id UUID,
    causation_id UUID,
    payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);

CREATE INDEX idx_outbox_unpublished
    ON outbox_events(occurred_at)
    WHERE published_at IS NULL;
