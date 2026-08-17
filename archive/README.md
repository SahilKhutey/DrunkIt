# Archive

This directory contains superseded, reference, or legacy code that has been
integrated into the canonical source tree or retired.

**Do not develop new features here.**
**Do not import from here in production code.**

---

## reference/

Reference implementations that served as staging areas during development.
The canonical versions of this code now live in `services/drunkit-mvp/` (backend)
and `apps/drunkit-web/` (frontend).

| Directory | Canonical Replacement | Archived |
|---|---|---|
| `drunkit-mvp-reference/` | `services/drunkit-mvp/` | 2026-08-16 |
| `drunkit-mvp1-reference/` | `services/drunkit-mvp/` | 2026-08-16 |
| `drunkit-web-reference/` | `apps/drunkit-web/` | 2026-08-16 |

## legacy-services/

Pre-registry service directories that predate the canonical `services/services.json`
naming convention (`foo` vs `foo-service`). The authoritative implementations are
the registered `foo-service` counterparts.

| Directory | Canonical Replacement | Archived |
|---|---|---|
| `catalogue/` | `services/catalog-service/` | 2026-08-16 |
| `compliance/` | `services/compliance-service/` | 2026-08-16 |
| `consumer/` | `services/consumer-service/` | 2026-08-16 |
| `delivery/` | `services/delivery-service/` | 2026-08-16 |
| `delivery-engine/` | `services/delivery-service/` (integrated) | 2026-08-16 |
| `dispatch-engine/` | `services/delivery-service/` (integrated) | 2026-08-16 |
| `event-worker/` | `services/_common/faccp_common/workers/` | 2026-08-16 |
| `fulfillment/` | `services/delivery-service/` | 2026-08-16 |
| `fulfilment-service/` | `services/delivery-service/` | 2026-08-16 |
| `governance/` | `services/_common/faccp_common/governance/` | 2026-08-16 |
| `identity/` | `services/identity-service/` | 2026-08-16 |
| `inventory/` | `services/inventory-service/` | 2026-08-16 |
| `observability/` | `services/_common/faccp_common/telemetry/` | 2026-08-16 |
| `order/` | `services/order-service/` | 2026-08-16 |
| `payment/` | `services/payment-service/` | 2026-08-16 |
| `resilience/` | `services/_common/faccp_common/resilience/` | 2026-08-16 |
| `risk/` | `services/risk-service/` | 2026-08-16 |
| `security/` | `services/_common/faccp_common/security/` | 2026-08-16 |
