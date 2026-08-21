# DrunkIt v0.1 — Architecture

## 1. Purpose

DrunkIt v0.1 is an Alcohol Discovery & Retail Availability Platform.

The MVP is **not** a delivery-first application. Its primary job is:

> Discover → Understand → Find → Verify → Connect

The initial transactional capability is limited to availability/retailer connection. Commerce is enabled only after jurisdiction-specific compliance requirements have been verified.

## 2. Architectural principles

1. PostgreSQL is the operational source of truth.
2. Redis is non-authoritative infrastructure for cache, rate limiting, sessions and ephemeral coordination.
3. FastAPI is initially the API gateway and modular backend.
4. Domain modules are separated internally before being extracted into services.
5. Shared API contracts are generated from/validated against OpenAPI and represented in `packages/types`.
6. Compliance is a platform primitive, not checkout middleware added later.
7. Regulatory rules are versioned data.
8. Commands that can create state changes must be idempotent.
9. Important asynchronous side effects use an outbox/event boundary.
10. No microservice extraction is performed without measured operational justification.

## 3. MVP logical architecture

```text
                       ┌──────────────────────┐
                       │   Consumer Web       │
                       │   Next.js + TS       │
                       └──────────┬───────────┘
                                  │
                       ┌──────────▼───────────┐
                       │   Retailer Web       │
                       │   Next.js + TS       │
                       └──────────┬───────────┘
                                  │
                           HTTPS / JSON
                                  │
                       ┌──────────▼───────────┐
                       │ FastAPI API           │
                       │ /api/v1               │
                       └──────────┬───────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       │                          │                          │
┌──────▼──────┐            ┌──────▼──────┐            ┌──────▼──────┐
│ PostgreSQL  │            │    Redis    │            │   Object    │
│ Source      │            │ Cache/TTL   │            │   Storage   │
│ of Truth    │            │ Ephemeral   │            │ S3-compatible│
└──────┬──────┘            └─────────────┘            └─────────────┘
       │
       ├── Catalog
       ├── Brand
       ├── Retailer
       ├── Inventory
       ├── Availability
       ├── Compliance
       ├── Identity
       └── Audit
       │
┌──────▼──────┐
│ Worker      │
│ Background  │
│ Jobs        │
└─────────────┘
```

## 4. Domain modules

### Identity
Users, credentials/session state, roles and access policies.

### Catalog
Brands, producers, products, variants, SKUs, categories and attributes.

### Discovery
Search, filters, collections, ranking and recommendation candidates.

### Retailer
Retailer onboarding, locations, licence metadata and retailer status.

### Inventory
Retailer SKU mappings, quantities, prices and freshness.

### Availability
The normalized answer to: "Can this product currently be found at this retailer/location?"

### Compliance
Jurisdictions, rules, rule versions, compliance checks and decisions.

### Audit
Append-only security/compliance/business audit records.

### Analytics
Interaction/event capture. Analytical processing remains asynchronous.

## 5. Request flow

```text
Client
  │
  ▼
Authentication / authorization
  │
  ▼
API validation
  │
  ▼
Domain service
  │
  ├── PostgreSQL transaction
  │
  ├── Outbox event
  │
  └── Redis cache invalidation where required
```

## 6. Discovery flow

```text
Query
  │
  ▼
Keyword / filter candidate retrieval
  │
  ▼
Product + retailer availability enrichment
  │
  ▼
Jurisdiction/compliance eligibility filtering
  │
  ▼
Ranking
  │
  ▼
Consumer result
```

Compliance and availability are not merely UI filters. The backend remains authoritative.

## 7. Availability model

Availability is derived from:

```text
Canonical Product
      +
Retailer SKU Mapping
      +
Inventory Snapshot
      +
Price
      +
Retailer Location
      +
Market/Jurisdiction
      =
Availability
```

Inventory freshness is explicitly tracked. Stale inventory must not be represented as confidently real-time.

## 8. Compliance model

Rules are data:

```text
Jurisdiction
   └── Rule Version
        └── Rule
             ├── Product restrictions
             ├── Consumer requirements
             ├── Retailer requirements
             ├── Ordering status
             ├── Delivery status
             └── Evidence/source
```

The engine returns a deterministic, auditable decision:

```text
ALLOW | DENY | REVIEW
```

with rule version and reason codes.

## 9. Event architecture

MVP uses PostgreSQL outbox records plus workers.

Future:

```text
PostgreSQL Outbox
       │
       ▼
Kafka / Redpanda
       │
 ┌─────┼─────────┐
 ▼     ▼         ▼
ML   Analytics  Notifications
```

Canonical event envelope:

```json
{
  "event_id": "uuid",
  "event_type": "PRODUCT_VIEWED",
  "schema_version": 1,
  "occurred_at": "ISO-8601",
  "actor_id": "uuid|null",
  "correlation_id": "uuid",
  "causation_id": "uuid|null",
  "payload": {}
}
```

## 10. Security

- HTTPS in deployed environments.
- Passwords are hashed with an approved password hashing algorithm.
- No raw card data is stored.
- Privileged roles require MFA.
- RBAC is enforced server-side.
- Sensitive operations are audited.
- PII is minimized.
- Secrets are environment/configuration managed.
- Rate limiting is applied to authentication and public APIs.
- Compliance decisions retain their rule version and evidence references.

## 11. Observability

Every service exposes:

- `/health`
- `/ready`
- `/version`

Application logs are structured JSON in production.

Future observability stack:

OpenTelemetry → Prometheus/Grafana + centralized logs.

## 12. Scalability path

### Stage 1
Next.js + FastAPI + PostgreSQL + Redis + object storage + worker.

### Stage 2
pgvector + OpenSearch + stronger analytics pipeline.

### Stage 3
Kafka/Redpanda + ClickHouse + horizontal worker/API scaling.

### Stage 4
Selective service extraction.

Kubernetes is intentionally deferred.

## 13. Architectural non-goals

v0.1 will not build:

- 20+ microservices
- custom payment gateway
- custom delivery fleet
- blockchain
- global multi-country infrastructure
- advanced LLM agent
- large recommendation model
- custom Kubernetes platform
