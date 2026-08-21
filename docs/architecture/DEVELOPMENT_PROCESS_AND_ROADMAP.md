# DrunkIt — Development Process, Phased Roadmap & Engineering Backlog

## Executive Overview

This document specifies the 10-Phase Engineering Roadmap, the MVP v0.1 Definition, Anti-Goals, Success Metrics, and Sprint Backlog for **DrunkIt**.

---

## 1. Ten-Phase Strategic Development Roadmap

```text
 PHASE 0: Legal, Regulatory & Product Foundation
 ├── State Regulatory Matrix codified as data (REGULATORY_MATRIX.md)
 ├── Canonical Domain Model & Entity Relationships (DOMAIN_MODEL.md)
 └── Multi-sided business model & compliance gates definition
       │
       ▼
 PHASE 1: Platform & Monorepo Foundation
 ├── Turborepo workspace, Next.js, FastAPI, PostgreSQL (FTS + pgvector), Redis, Docker
 ├── Shared contracts (packages/types) & OpenAPI generation
 └── Role-Based Access Control (Consumer, Retailer, Brand, Admin)
       │
       ▼
 PHASE 2: Canonical Product Catalogue
 ├── Brand & distillery profiles, canonical products, variants, SKUs
 ├── Taste taxonomy (384-dim taste vector embeddings) & ABV attributes
 └── High-performance product catalog browsing & search
       │
       ▼
 PHASE 3: Consumer Discovery Engine (The First Consumer Milestone)
 ├── Semantic taste search (*"peated single malt with fruity finish"*)
 ├── Occasion / Mood collections, filter matrix, brand stories
 └── Real-time nearby store inventory availability mapping
       │
       ▼
 PHASE 4: Retailer Network & Store Onboarding
 ├── Merchant onboarding & excise license verification
 ├── POS inventory normalizer, CSV import, manual stock dashboard
 └── Real-time store operating hours & geo-delivery radius locking
       │
       ▼
 PHASE 5: Regulatory Compliance Engine (FACCP Core)
 ├── Policy-as-code versioned YAML rules (e.g. IN-WB-2026-08-v1)
 ├── Zero-Knowledge age proof & statutory dry day enforcement
 └── Pre-checkout fail-closed decision API (`POST /compliance/check`)
       │
       ▼
 PHASE 6: Regulated Commerce Engine
 ├── Basket management, price lock, and payment provider abstraction
 ├── State-specific delivery dispatch & 3-point handover OTP gates
 └── Automated excise settlement & cancellation/refund sagas
       │
       ▼
 PHASE 7: Two-Sided Brand Platform
 ├── Brand self-service studio, SKU showcase, geo-availability heatmaps
 ├── New product launch campaigns & merchandising placements
 └── Direct consumer engagement metrics & review curation
       │
       ▼
 PHASE 8: Market & Demand Intelligence Platform
 ├── B2B SKU velocity, regional demand heatmaps, price elasticity
 └── Stockout prediction, flavor affinity shifts, and B2B SaaS feeds
       │
       ▼
 PHASE 9: Horizontal Scale & Distributed Systems
 ├── Kafka / Redpanda event streaming, ClickHouse analytics
 └── OpenSearch cluster & multi-region active-active primitives
       │
       ▼
 PHASE 10: Global Internationalization
 └── Country-specific regulatory adapters (US, UK, UAE, Australia, Mexico)
```

---

## 2. MVP Definition: DrunkIt v0.1 — Alcohol Discovery & Retail Availability

> **Target Outcome**: Build the **Discovery + Catalog + Retailer + Availability + Compliance Foundation** first.  
> The MVP proves that DrunkIt can efficiently connect consumers with discoverable, legitimate alcohol products and verified local licensed retail supply.

### MVP Scope Matrix
- **Consumer**: Geolocation detection $\to$ Browse/search catalog $\to$ Semantic taste filter $\to$ View brand stories $\to$ Check real-time store stock $\to$ Save favorites $\to$ Get store directions (Assisted) or initiate checkout (Transactional where legal).
- **Licensed Retailer**: Merchant registration $\to$ License upload $\to$ Store profile setup $\to$ Inventory ledger update (POS/CSV/Manual) $\to$ MRP price lock.
- **Admin**: Approve retailer licenses $\to$ Manage master products $\to$ Codify state excise rules $\to$ Merkle audit trail inspection.

---

## 3. What NOT to Build Yet (Anti-Goals for MVP)

```text
┌───────────────────────────────────────┬────────────────────────────────────────┐
│ ANTI-GOAL                             │ STRATEGIC RATIONALE                    │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ ❌ 20+ Independent Microservices       │ Massive operational overhead; modular  │
│                                       │ monolith inside FastAPI is optimal.    │
│ ❌ Custom Kubernetes Cluster          │ Docker Compose is sufficient for MVP.  │
│ ❌ Proprietary Delivery Bike Fleet     │ Leverage 3PL / Retailer delivery.      │
│ ❌ Custom Payment Gateway Hardware     │ Integrate standard UPI / PG SDKs.      │
│ ❌ Blockchain / Crypto Tokens          │ Pure overhead; SHA-256 Merkle log wins.│
│ ❌ Complex Social Network Features     │ Focus purely on discovery & trust.     │
│ ❌ Over-Engineered Recommendation ML  │ Start with rule-based + pgvector taste.│
└───────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 4. Engineering Sprint Backlog (Sprints 1 to 7+)

### Sprint 1: Foundation & Contracts
- [x] Monorepo workspace configuration (`pnpm` + Turborepo).
- [x] Next.js frontend + FastAPI backend + PostgreSQL + Redis environment.
- [x] Shared TypeScript contracts (`packages/types`) generated from Pydantic schemas.
- [x] Docker development environment.

### Sprint 2: Identity & Access Control
- [ ] Phone OTP consumer authentication.
- [ ] Email/Password + TOTP MFA for Retailers, Brand Managers, and Admins.
- [ ] Role-Based Access Control (RBAC) middleware.
- [ ] Privacy vault integration for consumer PII encryption.

### Sprint 3: Master Product Catalogue
- [ ] Brand, Producer, and Distillery entity models.
- [ ] Canonical Products, Variants (750ml, 375ml, 180ml), and SKUs.
- [ ] Flavor taxonomy and 384-dimensional taste vector generation (`all-MiniLM-L6-v2`).
- [ ] Catalog REST endpoints with PostgreSQL Full-Text Search.

### Sprint 4: Consumer Discovery Engine
- [ ] Semantic taste search with `pgvector` HNSW index.
- [ ] Occasion collections (*House Party, Date Night, Single Malt Connoisseur*).
- [ ] Next.js SSR Product Detail Pages with Rich Schema Markup (JSON-LD).
- [ ] Geolocation-based store distance calculation.

### Sprint 5: Retailer Network & Availability Graph
- [ ] Merchant registration and license verification workflow.
- [ ] Store location profiles and operating hours management.
- [ ] Inventory ledger endpoints (Stock count, reserved stock, MRP price).
- [ ] Inventory Normalizer pipeline for fuzzy SKU name matching.

### Sprint 6: Regulatory Engine & Compliance Decision API
- [ ] Declarative YAML policy loader (`policies/jurisdictions/IN-*.yaml`).
- [ ] `POST /api/v1/compliance/check` endpoint implementation.
- [ ] Zero-Knowledge statutory age verification evaluator.
- [ ] Dry Day calendar checker and operating hours lockout.
- [ ] SHA-256 Merkle audit event publisher.

### Sprint 7+: Regulated Commerce (Phase 1 Jurisdictions)
- [ ] Verified cart and session management.
- [ ] Server-side price integrity check.
- [ ] Escrow payment abstraction (UPI, Cards, NetBanking).
- [ ] Order fulfillment state machine and 3-point delivery OTP handoff.

---

## 5. Success Metrics & North Star

$$\text{North Star Metric} = \mathbf{\text{Successful Product-to-Consumer Connections (SPCC)}}$$

*A connection occurs when a consumer discovers an alcohol product, validates real-time local availability, and successfully connects to a licensed retailer (via in-store visit, click-and-collect, or digital delivery).*

### Key Performance Indicators (KPIs)

| Domain | Metric | Target |
| :--- | :--- | :--- |
| **Discovery** | Search-to-Product-View Rate | > 45% |
| **Discovery** | Zero-Search Result Rate | < 3.0% |
| **Catalog** | Taste Recommendation CTR | > 18% |
| **Retail** | Retailer Inventory Freshness | Sync $< 15$ mins |
| **Compliance** | Compliance Decision API Latency | $P_{99} < 25\text{ ms}$ |
| **Commerce** | Checkout Conversion Rate (where legal) | > 8.5% |
| **Trust** | Audit Hash Verification Pass Rate | 100.0% |
