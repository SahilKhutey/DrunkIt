# FACCP Catalog & Template Platform Architecture

## Executive Overview
The Catalog & Template Platform is the governance backbone that maintains consistency as the platform expands. It provides discoverability, governance, standardization, and rapid template-driven development across all 71 functional modules and 13 domains.

```
                 PLATFORM CATALOG SYSTEM
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ADMIN CATALOG    DEVELOPER CATALOG   TEMPLATE ENGINE
        │                │                │
        ▼                ▼                ▼
 Governance          APIs              Service
 Policies            Events            Domain
 Roles               Schemas           Workflow
 Jurisdictions       SDKs              UI
 Retailers           Components        Configuration
 Products            Integrations      Compliance
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                 CATALOG REGISTRY
                         │
                         ▼
                VERSION / VALIDATION
                         │
                         ▼
                  DEPLOYABLE SYSTEM
```

---

## 📊 The 4 Catalog Layers

1. **Administrative Catalog**: Control-plane catalog (`Organizations`, `Jurisdictions`, `Policies`, `Roles`, `Permissions`, `Workflows`, `Rules`, `Product Classifications`, `Retailers`, `Stores`).
2. **Developer Catalog**: Engineering control plane (`Services`, `APIs`, `Events`, `Schemas`, `Dependencies`, `Integrations`, `SDKs`, `Components`).
3. **Template Engine**: Codification & reuse engine producing standardized services, APIs, workflows, and frontend modules.
4. **Registry & Governance**: Versioning, validation engine, approval workflows, and lifecycle state tracking.

---

## 🏛️ Administrative Sub-Catalogs (10 Catalogs)

- **ADM-CAT-01 — Organization Catalog**: Platform-level legal entities, departments, and administrators (`POST /api/v1/catalog/organizations`).
- **ADM-CAT-02 — Jurisdiction Catalog**: Country → State → District → City → Zone boundary definitions and policy assignments.
- **ADM-CAT-03 — Policy Catalog**: Policy lifecycle (`DRAFT` → `REVIEW` → `APPROVED` → `SCHEDULED` → `ACTIVE` → `SUPERSEDED` → `ARCHIVED`).
- **ADM-CAT-04 — Role Catalog**: Central definitions for 16 platform roles (from `Consumer` to `Super Administrator`).
- **ADM-CAT-05 — Permission Catalog**: Granular resource-action permissions (e.g., `order.read`, `policy.activate`).
- **ADM-CAT-06 — Workflow Catalog**: Administrative workflows (Registration, License Approval, Policy Activation, Disputes).
- **ADM-CAT-07 — Compliance Rule Catalog**: Independently versioned atomic rules (e.g., Age limits, Dry day restrictions).
- **ADM-CAT-08 — Product Classification Catalog**: Category constraints, ABV limits, and jurisdiction suitability rules.
- **ADM-CAT-09 — Retailer Catalog**: Participating seller profiles, legal licenses, and compliance standings.
- **ADM-CAT-10 — Store Catalog**: Physical & digital store locations, operating hours, and geofenced delivery zones.

---

## 💻 Developer Sub-Catalogs (8 Catalogs)

- **DEV-CAT-01 — Service Catalog**: Backend service identities, database links, event dependencies, and K8s deployment topology.
- **DEV-CAT-02 — API Catalog**: OpenAPI endpoint contracts, auth requirements, rate limits, and correlation headers.
- **DEV-CAT-03 — Event Catalog**: CloudEvent topic definitions, producer/consumer mappings, and schema references.
- **DEV-CAT-04 — Schema Catalog**: Versioned data contracts (`schemas/consumer/`, `schemas/order/`, etc.).
- **DEV-CAT-05 — Service Dependency Catalog**: Machine-readable service dependency graph and blast-radius map.
- **DEV-CAT-06 — Integration Catalog**: Third-party integration provider registry (Razorpay, Onfido, Twilio, S3).
- **DEV-CAT-07 — SDK Catalog**: Registered client SDKs (Python, TypeScript, Mobile, Partner).
- **DEV-CAT-08 — Component Catalog**: Reusable engineering components (Auth modules, Kafka clients, DB adapters).

---

## ⚙️ Template Engine & Golden Templates

### 12 Core Templates
1. Service Template (FastAPI Python)
2. Detailed FastAPI Architecture Template
3. Next.js Application Template
4. API Resource Template
5. Event Specification Template
6. Workflow Engine Template
7. RBAC Definition Template
8. Database & Repository Template
9. Integration Adapter Template
10. Compliance Module Template
11. Admin UI & API Module Template
12. Consumer Feature Module Template

### 7 Golden Templates (Architectural Standard)
Changes to Golden Templates require explicit Architecture + Security review:
- `Secure API (Golden)`
- `Secure Service (Golden)`
- `Compliance Service (Golden)`
- `Payment Service (Golden)`
- `Identity Service (Golden)`
- `Audit Service (Golden)`
- `Integration Service (Golden)`

---

## 🔍 Catalog Validation Engine

Before any catalog object transitions to `ACTIVE`, it must pass 7 validation stages:
1. **Schema Validation**: Syntactic definition correctness.
2. **Dependency Validation**: Verification that all required downstream/upstream services exist and are compatible.
3. **Security Validation**: Verification of authentication, authorization, and secret standards.
4. **Permission Validation**: Granular action permission assignment.
5. **Compliance Validation**: Compliance policy requirement matching.
6. **Compatibility Validation**: Backwards-compatibility checks.
7. **Approval**: Explicit sign-off by an authorized role (`Architect`, `Security`, `Compliance`).
