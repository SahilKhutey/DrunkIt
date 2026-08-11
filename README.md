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
$env:PYTHONPATH="$PWD\services\_common;$PWD\services\developer-portal"
.\.venv\Scripts\python.exe -m pytest tests\unit\test_phase4.py tests\unit\test_phase5.py -q -p no:cacheprovider
```

For services that use the local package name `app`, run focused tests with only that service on `PYTHONPATH` to avoid importing the wrong service package.

## Current Development Status

The codebase contains production-oriented foundations, but it should still be treated as an active development repository. Several services are functional cores or scaffolded service foundations rather than fully deployed production services. Before launch, run a dedicated integration pass for:

- Docker Compose service coverage and port consistency.
- Python dependency installation and reproducible test environment.
- Database migrations for newer services.
- Secrets management and production configuration hardening.
- End-to-end compliance, payment, verification, and delivery flows.
- Legal review of licensing, privacy, and regulated-commerce obligations.

## Documentation

- [Architecture](./docs/architecture/Architecture.md)
- [Development Status](./docs/DEVELOPMENT_STATUS.md)
- [Operations Deployment](./docs/operations/Deployment.md)
- [Privacy Architecture](./docs/privacy/Privacy-Architecture.md)
- [Regulatory Model](./docs/compliance/Regulatory-Model.md)
- [Commercialization Guide](./COMMERCIALIZATION.md)

## Commercial Use

Commercial use is restricted. To license, resell, host, white-label, integrate, or otherwise commercialize DrunkIt/FACCP, obtain written authorization from Sahil Khutey.
