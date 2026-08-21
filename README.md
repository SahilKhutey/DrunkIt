# DrunkIt / FACCP

DrunkIt is the working repository for FACCP: the Federated Alcohol Commerce, Compliance & Trust Platform. It is an enterprise platform for regulated alcohol commerce, built around age eligibility, jurisdiction-aware compliance, privacy-preserving identity handling, retailer licensing, delivery verification, auditability, and white-label commercialization.

The platform is structured as a monorepo with Python microservices, shared packages, web apps, mobile app foundations, policies, infrastructure, and operational documentation.

## Ownership And License

This repository is proprietary commercial software owned by Sahil Khutey. All rights are reserved. No rights are granted to use, copy, modify, distribute, sublicense, host, sell, or commercialize this software unless Sahil Khutey provides explicit written permission or a signed commercial agreement.

See [LICENSE](./LICENSE) and [COMMERCIALIZATION.md](./COMMERCIALIZATION.md).

## Platform Capabilities

- Identity, age eligibility, MFA, RBAC, ABAC, and privacy controls.
- Consumer, retailer, catalog, inventory, order, payment, delivery, notification, compliance, audit, risk, verification, analytics, pricing, recommendation, real-time, white-label, developer portal, CDP, and marketing service foundations.
- Jurisdiction-aware compliance policy evaluation for regulated product commerce.
- Hash-chained audit foundations for tamper-evident event trails.
- Multi-region active-active primitives with CRDTs, vector clocks, and region routing.
- White-label tenant, theme, domain, and configuration management.
- Developer marketplace core with API products, API key issuance, subscription limits, and usage metering.
- Customer Data Platform core with identity resolution, consent-aware segmentation, and audience export.
- Marketing automation core with campaign planning, frequency caps, A/B allocation, and journey scheduling.
- Web and mobile app foundations for admin, retailer, consumer, and delivery workflows.

## Repository Layout

```text
apps/                  Web and mobile application frontends
docs/                  Architecture, compliance, operations, privacy, and commercialization docs
infrastructure/         Docker, Kubernetes, monitoring, database, and recovery assets
packages/               Shared TypeScript packages and UI components
policies/               Jurisdiction and compliance policy data
services/               Python microservices and shared backend library
tests/                  Unit tests for platform services and shared modules
```

## DrunkIt Core Systems

The platform includes a complete, end-to-end slice of the regulated alcohol commerce stack:

1. **DrunkIt MVP Backend (`services/drunkit-mvp`)**: FastAPI service (port `8000`) with phone OTP consumer auth, bcrypt staff auth (`PLATFORM_ADMIN` vs `RETAILER_STAFF`), state jurisdiction eligibility engine, fail-closed listing engine, server-side verified checkout, delivery state machine with handoff verification gates, and Alembic migrations.
2. **DrunkIt Consumer Web (`apps/drunkit-web`)**: Vite + React + Tailwind storefront (port `5173`) with bottle-glass ink palette, excise duty seal badge, age verification, location/catalog discovery, cart, checkout, and real-time delivery tracking.
3. **DrunkIt Staff Console (`apps/drunkit-staff`)**: Vite + React + Tailwind operations dashboard (port `5174`) with role-adaptive views for platform admins (retailers, staff onboarding, shared product catalog, delivery dispatch) and retailer staff (store management, listings, orders).

### Quick Start (Full DrunkIt Stack)

Start the entire DrunkIt stack with Docker Compose:

```bash
docker compose --profile core up --build
```

Or run services locally:

```bash
# 1. Backend MVP API (port 8000)
cd services/drunkit-mvp
python -m scripts.seed   # Seeds demo catalog and staff accounts
uvicorn app.main:app --reload --port 8000

# 2. Consumer Web App (port 5173)
pnpm dev:web

# 3. Staff Operations Console (port 5174)
pnpm dev:staff
```

## Local Development

Install frontend workspace dependencies:

```bash
pnpm install
```

Start local infrastructure:

```bash
docker compose up -d
```

Run frontend development tasks:

```bash
pnpm dev
```

Run focused Python tests from PowerShell:

```powershell
$env:PYTHONPATH="$PWD\services\drunkit-mvp"
.\.venv\Scripts\python.exe -m pytest services\drunkit-mvp\tests -v
```

## Current Development Status

The codebase contains production-oriented foundations, but it should still be treated as an active development repository. Several services are functional cores or scaffolded service foundations rather than fully deployed production services. Before launch, run a dedicated integration pass for:

- Docker Compose service coverage and port consistency.
- Python dependency installation and reproducible test environment.
- Database migrations for newer services.
- Secrets management and production configuration hardening.
- End-to-end compliance, payment, verification, and delivery flows.
- Legal review of licensing, privacy, and regulated-commerce obligations.

## Documentation & Strategic Architecture

- **Strategy & Rebrand**: [Strategic Rebrand & Architecture Blueprint](./docs/strategy/STRATEGIC_REBRAND_AND_ARCHITECTURE.md)
- **Product Architecture & Stack v1.0**: [Product Architecture & Technology Stack v1.0](./docs/architecture/PRODUCT_ARCHITECTURE_AND_TECH_STACK_V1.md)
- **Core Domain Model**: [Domain Model & Entity Relationships](./docs/architecture/DOMAIN_MODEL.md)
- **Roadmap & Sprints**: [Development Process, Phased Roadmap & Engineering Backlog](./docs/architecture/DEVELOPMENT_PROCESS_AND_ROADMAP.md)
- **Indian Market & SAM**: [Indian Alcohol Market Sizing & Regulatory SAM/TAM Model](./docs/research/INDIA_ALCOHOL_MARKET_AND_SAM_ANALYSIS.md)
- **Global Indie Market**: [Global Independent & Craft Alcohol Analysis (2026)](./docs/research/GLOBAL_INDEPENDENT_AND_LOCAL_ALCOHOL_MARKET.md)
- **Regulatory Matrix as Code**: [State Regulatory Matrix as Code](./docs/compliance/REGULATORY_MATRIX.md)
- **Compliance Engine Spec**: [Regulatory Engine & Compliance Decision API](./docs/compliance/REGULATORY_ENGINE_SPEC.md)
- **Platform Microservices**: [Platform System Architecture](./docs/architecture/Architecture.md)
- **Development Status**: [Development Status](./docs/DEVELOPMENT_STATUS.md)
- **Operations & Deployment**: [Operations Deployment](./docs/operations/Deployment.md)
- **Privacy & Trust**: [Privacy Architecture](./docs/privacy/Privacy-Architecture.md)
- **Commercialization**: [Commercialization Guide](./COMMERCIALIZATION.md)

## Commercial Use

Commercial use is restricted. To license, resell, host, white-label, integrate, or otherwise commercialize DrunkIt/FACCP, obtain written authorization from Sahil Khutey.
