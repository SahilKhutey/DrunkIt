# Development Status

This repository contains a large enterprise platform foundation for regulated alcohol commerce. It includes working domain cores, service scaffolds, frontend foundations, policy data, infrastructure assets, and focused tests.

## Implemented Foundations

- Core commerce services: identity, consumer, retailer, catalog, inventory, order, payment, pricing, delivery, notification, compliance, audit, risk, verification, analytics, recommendation, real-time, white-label, developer portal, CDP, and marketing.
- Shared backend utilities for events, DTOs, middleware, privacy, ABAC, federation, sagas, replication, logging, and Kafka clients.
- Multi-region primitives with CRDT counters, observed-remove sets, registers, vector clocks, and region selection.
- White-label service API for tenants, themes, domains, verification, and tenant configuration.
- Developer portal API marketplace core for API products, API keys, subscriptions, usage metering, and quota decisions.
- Customer Data Platform core for identity resolution, consent scopes, segmentation, and audience export.
- Marketing automation core for campaign targeting, frequency capping, deterministic A/B assignment, and journey scheduling.

## Known Gaps

- The local `.venv` is missing several backend dependencies used by full service apps, including packages such as SQLAlchemy, structlog, aiokafka, prometheus-client, and pytest-asyncio.
- Some services are domain-complete or API-sandboxed but still need persistent database models, migrations, and integration tests.
- Docker Compose needs an integration pass for complete service coverage, consistent ports, health checks, and dependency wiring.
- Several newer services are not yet wired into central routing, monitoring, database initialization, and deployment manifests.
- Existing architecture documentation contains some encoding damage in older diagrams and should be refreshed into Mermaid or generated diagrams.

## Recommended Stabilization Order

1. Establish an authoritative service registry covering names, ports, Dockerfiles, databases, health endpoints, and gateway routes.
2. Normalize service layout and packaging across legacy and newer service styles.
3. Install and lock Python service dependencies so test runs are reproducible.
4. Add Alembic migrations for new database-backed services.
5. Wire Docker Compose, monitoring, and database initialization for new services.
6. Add end-to-end flows for age verification, compliance decisioning, payment, delivery, audit, white-label tenant resolution, developer API access, CDP segmentation, and marketing activation.
7. Complete production hardening: secrets, CORS, TLS, observability, retention, audit policies, backup drills, and incident response.

## Verification Snapshot

Focused tests recently added and verified:

```text
tests/unit/test_phase4.py
tests/unit/test_phase5.py
tests/unit/test_phase6.py
tests/unit/test_phase6_marketing.py
```

Because multiple services use the package name `app`, run tests with the target service on `PYTHONPATH` rather than placing every service on `PYTHONPATH` at once.
