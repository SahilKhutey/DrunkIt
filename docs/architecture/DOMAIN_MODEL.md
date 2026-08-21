# DrunkIt — Core Domain Model & Entity Relationship Specification

## Executive Overview

This document specifies the authoritative domain model, entity relationships, database tables, and schema constraints for **DrunkIt (FACCP Core)**.

The domain model reflects the fundamental backbone:
$$\text{Brand} \longrightarrow \text{Products} \longrightarrow \text{Variants} \longrightarrow \text{SKUs} \longrightarrow \text{Markets} \longrightarrow \text{Retailers} \longrightarrow \text{Inventory} \longrightarrow \text{Consumer} \longrightarrow \text{Order}$$

---

## 1. Domain Model Architecture Diagram

```text
 ┌─────────────────┐       ┌─────────────────┐
 │   BrandOwner    │       │    Producer     │
 └────────┬────────┘       └────────┬────────┘
          │ 1:N                     │ 1:N
          ▼                         ▼
   ┌──────────────┐          ┌──────────────┐
   │    Brand     │──────────│ Distributor  │
   └──────┬───────┘          └──────────────┘
          │ 1:N
          ▼
   ┌──────────────┐          ┌──────────────────────┐
   │   Product    │◄─────────│ Category/TasteProfile│
   └──────┬───────┘          └──────────────────────┘
          │ 1:N
          ▼
   ┌──────────────┐          ┌──────────────────────┐
   │ProductVariant│─────────►│     Canonical SKU    │
   └──────┬───────┘          └──────────┬───────────┘
          │                             │ 1:N
          │                             ▼
          │                  ┌──────────────────────┐
          │                  │      Inventory       │◄─────────┐
          │                  └──────────┬───────────┘          │
          │                             │                      │ 1:N
          │                             ▼                      │
   ┌──────┴───────┐          ┌──────────────────────┐   ┌──────────────┐
   │    Market    │◄─────────│   RetailerLocation   │◄──│   Retailer   │
   │ (State/Geo)  │          └──────────────────────┘   └──────┬───────┘
   └──────┬───────┘                                            │ 1:N
          │                                                    ▼
          │                                             ┌──────────────┐
          │                                             │RetailerLicence│
          ▼                                             └──────────────┘
   ┌──────────────┐
   │ComplianceRule│
   └──────┬───────┘
          │
          ▼
┌──────────────────┐
│ComplianceDecision│
└─────────┬────────┘
          │ Evaluates Before Checkout
          ▼
   ┌──────────────┐          ┌──────────────────────┐
   │     User     │─────────►│   ConsumerProfile    │
   └──────┬───────┘          └──────────────────────┘
          │ 1:N
          ▼
   ┌──────────────┐          ┌──────────────────────┐
   │    Order     │─────────►│   Payment & Refund   │
   └──────┬───────┘          └──────────────────────┘
          │ 1:N
          ▼
   ┌──────────────┐          ┌──────────────────────┐
   │  OrderItem   │          │   Delivery & Agent   │
   └──────────────┘          └──────────────────────┘
```

---

## 2. Core Domain Entity Specifications

### 2.1 Identity & User Domain
- **`User`**: Base authentication actor (Consumer, Retailer Staff, Brand Manager, Platform Admin).
  - Attributes: `id (UUID)`, `phone`, `email`, `role`, `is_active`, `mfa_enabled`, `created_at`, `updated_at`.
- **`ConsumerProfile`**: Privacy-isolated profile containing demographic claims and zero-knowledge age proofs.
  - Attributes: `id (UUID)`, `user_id (FK)`, `encrypted_pii_vault_id`, `state_residence`, `zk_age_proof_hash`, `age_eligibility_tier`, `preferred_flavors (JSONB)`.

### 2.2 Brand & Producer Domain
- **`BrandOwner`**: Corporate parent entity (e.g., Piccadily Agro, Radico Khaitan, Allied Blenders).
  - Attributes: `id (UUID)`, `company_name`, `country_code`, `tax_id`, `verification_status`.
- **`Brand`**: Consumer-facing brand house (e.g., *Indri, Glenwalk, Amrut, D'YAVOL*).
  - Attributes: `id (UUID)`, `owner_id (FK)`, `name`, `slug`, `story_markdown`, `hero_image_url`, `origin_country`, `origin_state`, `is_featured`.
- **`Producer` / `Distributor`**: Production facility or registered wholesale distributor.
  - Attributes: `id (UUID)`, `name`, `license_number`, `territory_codes (ARRAY)`, `contact_details (JSONB)`.

### 2.3 Catalog & Taste Taxonomy Domain
- **`Category` & `SubCategory`**: Structural classification (`Spirits` $\to$ `Single Malt Whisky`, `Gin`, `Agave`, `RTD`, `No/Low`).
- **`Product`**: Canonical product entity.
  - Attributes: `id (UUID)`, `brand_id (FK)`, `category_id (FK)`, `name`, `description`, `abv_percentage`, `cask_type`, `age_years`, `tasting_notes (JSONB)`, `taste_embedding (VECTOR(384))`.
- **`ProductVariant`**: Packaging and volume variation.
  - Attributes: `id (UUID)`, `product_id (FK)`, `volume_ml (750, 375, 180, etc.)`, `packaging_type (Glass Bottle, Gift Box, Can)`, `is_active`.
- **`SKU`**: Barcode/GTIN-level canonical stock keeping unit.
  - Attributes: `id (UUID)`, `variant_id (FK)`, `gtin_ean`, `excise_brand_code`, `status`.
- **`TasteProfile`**: Structured flavor vector (smoky, peaty, floral, citrus, sweet, oak, spicy, finish).

### 2.4 Geography & Market Domain
- **`Country`**: Sovereign legal boundary (`IND`, `USA`, `GBR`, `ARE`).
- **`State`**: State/provincial regulatory jurisdiction (e.g., `IN-WB`, `IN-MH`, `IN-KA`, `IN-DL`).
  - Attributes: `state_code (PK)`, `name`, `statutory_drinking_age`, `digital_delivery_authorized (BOOLEAN)`, `assisted_commerce_authorized (BOOLEAN)`, `current_policy_version`.
- **`Market`**: Municipal or city-level commercial cluster (e.g., `KOLKATA_METRO`, `MUMBAI_MMR`, `BENGALURU_URBAN`).

### 2.5 Retailer & Inventory Domain
- **`Retailer`**: Licensed retail business organization.
  - Attributes: `id (UUID)`, `legal_name`, `trade_name`, `pan_number`, `gstin`, `status (PENDING, APPROVED, SUSPENDED)`.
- **`RetailerLocation`**: Physical retail store outlet.
  - Attributes: `id (UUID)`, `retailer_id (FK)`, `state_code (FK)`, `address_line`, `city`, `pincode`, `latitude`, `longitude`, `delivery_radius_km`, `operating_hours (JSONB)`, `is_accepting_orders`.
- **`RetailerLicence`**: State excise operating license.
  - Attributes: `id (UUID)`, `location_id (FK)`, `license_number`, `license_category (e.g. FL-OFF, L-2, CS-2)`, `valid_from`, `valid_to`, `verified_by_admin_id`.
- **`Inventory`**: Real-time stock ledger per retail location.
  - Attributes: `id (UUID)`, `location_id (FK)`, `sku_id (FK)`, `stock_quantity`, `reserved_quantity`, `price_mrp`, `price_discounted`, `last_synced_at`, `sync_source (POS, CSV, MANUAL)`.
- **`InventorySnapshot`**: Historical audit snapshots for demand forecasting.

### 2.6 Regulatory & Compliance Domain
- **`ComplianceRule`**: Machine-readable statutory rule.
  - Attributes: `id (UUID)`, `jurisdiction_code`, `rule_version`, `rule_type (AGE_LIMIT, DRY_DAY, POSSESSION_LIMIT, OPERATING_HOURS)`, `parameters (JSONB)`, `effective_from`, `effective_to`.
- **`ComplianceDecision`**: Immutable record of transaction evaluation.
  - Attributes: `id (UUID)`, `order_intent_id`, `actor_user_id`, `jurisdiction_code`, `rule_version`, `decision (ALLOW, DENY)`, `reason_codes (ARRAY)`, `evaluated_at`, `hash_signature`.

### 2.7 Commerce & Order Domain
- **`Cart` & `CartItem`**: Transient basket tied to a specific retail location and verified user session.
- **`Order`**: Authoritative transactional contract.
  - Attributes: `id (UUID)`, `order_number`, `consumer_id (FK)`, `retailer_location_id (FK)`, `compliance_decision_id (FK)`, `state (PENDING_COMPLIANCE, AWAITING_PAYMENT, ACCEPTED_BY_RETAILER, PACKED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED)`, `gross_amount`, `discount_amount`, `delivery_fee`, `platform_fee`, `net_amount`, `created_at`.
- **`OrderItem`**: Specific SKU, quantity, unit price, and batch identification.
- **`Payment` & `Refund`**: Escrow and settlement transaction ledger.

### 2.8 Fulfillment & Trust Domain
- **`Delivery`**: Logistics task with 3-point verification (Merchant Handover OTP $\to$ In-Transit GPS $\to$ Consumer Recipient Age Check & Delivery OTP).
- **`AuditLog`**: Merkle-hash chained immutable security trail (`event_hash = SHA256(prev_hash + payload)`).

---

## 3. Database Schema DDL (PostgreSQL 16 + pgvector)

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Brands Table
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    origin_country VARCHAR(3) NOT NULL DEFAULT 'IND',
    origin_state VARCHAR(10),
    story_markdown TEXT,
    hero_image_url VARCHAR(1024),
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_brands_slug ON brands(slug);

-- 2. Products Table (with pgvector for Taste Intelligence)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE RESTRICT_MODE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    abv_percentage NUMERIC(4, 2) NOT NULL,
    age_years INT,
    description TEXT,
    tasting_notes JSONB DEFAULT '{}'::jsonb,
    taste_embedding vector(384),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_category ON products(category, sub_category);
-- HNSW Index for ultra-fast Approximate Nearest Neighbor vector search
CREATE INDEX idx_products_taste_embedding ON products 
USING hnsw (taste_embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 3. Product SKUs
CREATE TABLE product_skus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    volume_ml INT NOT NULL,
    packaging_type VARCHAR(50) NOT NULL DEFAULT 'BOTTLE',
    gtin_ean VARCHAR(50),
    excise_brand_code VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_product_volume UNIQUE (product_id, volume_ml)
);

-- 4. Retailer Locations
CREATE TABLE retailer_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_name VARCHAR(255) NOT NULL,
    state_code VARCHAR(10) NOT NULL,
    city VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    delivery_radius_km NUMERIC(4, 1) NOT NULL DEFAULT 5.0,
    license_number VARCHAR(100) NOT NULL,
    license_valid_to DATE NOT NULL,
    is_accepting_orders BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_retailer_geo ON retailer_locations(state_code, city);

-- 5. Inventory Ledger
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES retailer_locations(id) ON DELETE CASCADE,
    sku_id UUID NOT NULL REFERENCES product_skus(id) ON DELETE RESTRICT,
    stock_quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    price_mrp NUMERIC(10, 2) NOT NULL,
    last_synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_location_sku UNIQUE (location_id, sku_id),
    CONSTRAINT chk_stock_non_negative CHECK (stock_quantity >= 0),
    CONSTRAINT chk_reserved_valid CHECK (reserved_quantity >= 0 AND reserved_quantity <= stock_quantity)
);
CREATE INDEX idx_inventory_lookup ON inventory(location_id, sku_id);

-- 6. Compliance Decisions (Immutable Audit Gate)
CREATE TABLE compliance_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    location_id UUID NOT NULL REFERENCES retailer_locations(id),
    jurisdiction_code VARCHAR(10) NOT NULL,
    rule_version VARCHAR(50) NOT NULL,
    decision VARCHAR(20) NOT NULL, -- ALLOW / DENY
    reason_codes JSONB NOT NULL DEFAULT '[]'::jsonb,
    payload_snapshot JSONB NOT NULL,
    hash_signature VARCHAR(64) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_compliance_user_eval ON compliance_decisions(user_id, evaluated_at);

-- 7. Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    location_id UUID NOT NULL REFERENCES retailer_locations(id),
    compliance_decision_id UUID NOT NULL REFERENCES compliance_decisions(id),
    order_mode VARCHAR(30) NOT NULL DEFAULT 'HOME_DELIVERY', -- HOME_DELIVERY / CLICK_AND_COLLECT
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_PAYMENT',
    subtotal_amount NUMERIC(10, 2) NOT NULL,
    delivery_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    taxes_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_orders_user ON orders(user_id, status);
CREATE INDEX idx_orders_location ON orders(location_id, status);
```
