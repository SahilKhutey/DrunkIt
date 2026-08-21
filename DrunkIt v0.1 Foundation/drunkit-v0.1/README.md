# DrunkIt v0.1 Platform

> **Alcohol Commerce & Intelligence Platform connecting consumers, craft brands, licensed retailers, distributors, and deterministic state compliance engines.**

---

## Architecture Overview

DrunkIt v0.1 is structured as a high-performance **Modular Monolith & Monorepo** architecture transitioning gracefully towards distributed event-driven microservices.

```text
drunkit-v0.1/
├── apps/
│   ├── consumer-web/        # Next.js Consumer Discovery, 6-Axis Taste Radar & Availability UI (:3000)
│   ├── retailer-portal/     # Next.js Licensed Store POS Sync & Order Fulfillment Station (:3001)
│   ├── brand-portal/        # Next.js Distillery Brand Intelligence & Sensory Benchmarking (:3002)
│   └── driver-app/          # Next.js Mobile Driver Doorstep ID Verification & Handover (:3003)
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI routes: auth, catalog, discovery, compliance, commerce, retailer, brand, delivery
│   │   ├── core/            # Middleware, Correlation IDs, Error Handlers, Security & RBAC Guards
│   │   ├── db/              # SQLAlchemy session, Repository, Unit of Work, Master Seed Data
│   │   ├── models/          # Identity, Catalog, Retailer, Inventory, Pricing, Compliance, Commerce, Audit/Outbox
│   │   ├── schemas/         # Strict Pydantic v2 schemas and validation models
│   │   ├── services/        # Domain business logic: Identity, Catalog, Discovery, Compliance, Commerce, Delivery
│   │   └── workers/         # Transactional Outbox Relay Worker daemon for asynchronous event dispatch
│   ├── policies/            # Versioned Regulatory YAML Rule Packs (IN-WB, IN-MH, IN-KA, IN-DL, IN-GA)
│   └── tests/               # 72 comprehensive automated unit and E2E integration tests (100% green)
├── packages/
│   ├── types/               # Canonical TypeScript domain models and API contracts
│   ├── api-client/          # Universal typed HTTP SDK for DrunkIt v0.1 API
│   ├── ui/                  # Accessible luxury dark-theme design primitives (Button, Badge, Card)
│   └── validation/          # Edge and client-side runtime validation schemas
└── docker-compose.yml       # Production/development Docker Compose orchestration
```

---

## Key Platform Capabilities

1. **6-Axis Semantic Taste Intelligence**:
   - Vector space matching using Cosine Similarity against flavor dimensions: `Body`, `Sweetness`, `Smokiness`, `Bitterness`, `Fruitiness`, `Spiciness`.
   - Dynamic explainable match reasons generator and category benchmarking against peer spirits.
2. **Deterministic Regulatory & Compliance Engine**:
   - 100% deterministic evaluation of state-level excise regulations across West Bengal (`IN-WB`), Maharashtra (`IN-MH`), Karnataka (`IN-KA`), Delhi NCT (`IN-DL`), and Goa (`IN-GA`).
   - Automated evaluation of Legal Drinking Age (LDA), gazetted Dry Days calendar, operational hours (with timezone conversion to `Asia/Kolkata`), possession volume limits, licensed retailer validity, and delivery channel permissions.
3. **Retailer POS Mapping & Live Availability**:
   - Reconciles store POS barcodes and external SKUs with master canonical spirits.
   - Haversine geospatial proximity sorting with live statutory MRP pricing.
4. **Order Fulfillment State Machine**:
   $$\text{PENDING} \longrightarrow \text{CONFIRMED} \longrightarrow \text{PREPARING} \longrightarrow \text{READY\_FOR\_PICKUP} \longrightarrow \text{OUT\_FOR\_DELIVERY} \longrightarrow \text{FULFILLED}$$
5. **Doorstep Handover & Point-of-Delivery Verification**:
   - Physical government ID inspection ($21+$ verification), 4-digit OTP authentication, and fail-closed statutory abortion protocols.
6. **Transactional Outbox Event Pattern**:
   - Guaranteed at-least-once domain event streaming (`ORDER_CREATED`, `ORDER_STATUS_CHANGED`, `DELIVERY_HANDOVER_COMPLETED`, `INVENTORY_FEED_SYNCED`).

---

## Quick Start & Local Execution

### 1. Docker Compose Multi-Service Environment

```bash
docker compose up --build
```

Starts:
- **PostgreSQL 17** (`:5432`)
- **Redis 8** (`:6379`)
- **MinIO Object Storage** (`:9000`, Console `:9001`)
- **FastAPI Modular Monolith API** (`:8000`)
- **Outbox Relay Daemon Worker** (Background)

### 2. Run Backend Locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .[dev]

# Seed Master Indian Spirits Catalog & Pilot Store Network
python -c "from app.db.session import sync_session_factory; from app.db.seed import seed_master_catalog; session = sync_session_factory(); seed_master_catalog(session); session.close()"

# Start API Server
uvicorn app.main:app --reload --port 8000
```

### 3. Run Monorepo Frontend Applications

```bash
pnpm install

# Run Consumer Web App (:3000)
pnpm --filter @drunkit/consumer-web dev

# Run Retailer Store Portal (:3001)
pnpm --filter @drunkit/retailer-portal dev

# Run Brand House Intelligence Portal (:3002)
pnpm --filter @drunkit/brand-portal dev

# Run Driver Mobile Handover App (:3003)
pnpm --filter @drunkit/driver-app dev
```

---

## Automated Test Verification

Run the complete test suite (72 tests, 100% green):

```powershell
$env:PYTHONPATH="$PWD\backend"
.\.venv\Scripts\python.exe -m pytest backend\tests -v
```

---

## Ownership & Commercial License

This repository is proprietary commercial software owned by **Sahil Khutey**. All rights reserved.
