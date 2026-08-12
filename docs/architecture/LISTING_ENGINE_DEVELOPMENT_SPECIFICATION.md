# FACCP Listing Engine Development Specification

## Executive Overview
The Listing Engine is an independent platform service acting as a **read-optimized composition and policy-projection engine**. It owns no underlying truth database, but composes authorized views from independent, single-source-of-truth services (Catalog, Inventory, Pricing, Fulfilment, Compliance).

```
                         ┌─────────────────────┐
                         │   PRODUCT CATALOG   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │    LISTING ENGINE   │
                         └──────────┬──────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   Template Engine          Eligibility Engine          Action Engine
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                     ┌──────────────▼──────────────┐
                     │       VIEW COMPOSER         │
                     └──────────────┬──────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
         Product Card          Search Result         Product Detail
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                            CONSUMER API
                                    │
                      ┌─────────────┼─────────────┐
                      ▼             ▼             ▼
                    Web           Mobile        Partner
```

---

## ⚡ Core Equation & Pipeline

```text
Product Master + SKU/Variant + Retailer Listing + Inventory + Price + Serviceability + Fulfilment + Policy State + User Context
   = Listing Engine Composed View Model
```

---

## 📦 17 Core Service Modules

1. `catalog`: Product/SKU catalog client adapter.
2. `listings`: Listing domain model & status state machine.
3. `templates`: Config-driven listing template registry.
4. `rendering`: Field-level view composer engine.
5. `availability`: Real-time stock status calculator.
6. `pricing`: Pricing engine client adapter.
7. `fulfilment`: Serviceability zone & delivery ETA calculator.
8. `eligibility`: Policy & jurisdiction compliance adapter.
9. `actions`: Server-side action authorization engine (`view`, `add_to_cart`, `purchase`).
10. `ranking`: Multi-store deterministic ranking & filter pipeline.
11. `search`: Search index query adapter.
12. `personalization`: Policy-controlled recommendation engine.
13. `caching`: Multi-tier Redis & API cache strategy.
14. `events`: Asynchronous CloudEvent listeners & invalidators.
15. `analytics`: Privacy-safe telemetry emitters.
16. `validation`: Schema & DTO validators.
17. `audit`: Administrative action audit logger.

---

## 🔄 Separation of Dimensions: Listing Lifecycle vs Inventory Status

| Dimension | States | Description |
|---|---|---|
| **Listing Lifecycle** | `DRAFT`, `VALIDATING`, `READY`, `ACTIVE`, `PAUSED`, `SUSPENDED`, `ARCHIVED` | Administrative / Governance state |
| **Inventory Status** | `IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`, `UNKNOWN` | Stock availability state |

*Critical Rule*: A listing remains `ACTIVE` even when inventory reaches 0 (`ACTIVE` + `OUT_OF_STOCK`).

---

## 📐 8 Template Types

1. `CARD`: Compact product card.
2. `GRID_CARD`: Grid layout card.
3. `LIST_CARD`: List view card.
4. `SEARCH_RESULT`: Search result display.
5. `PRODUCT_DETAIL`: Full product page.
6. `CATEGORY_RESULT`: Category page result.
7. `STORE_PRODUCT`: Store-specific listing.
8. `RECOMMENDATION_CARD`: Related product card.

---

## 🛡️ Fail-Closed Fault Tolerance

If an upstream dependency fails:
- **Inventory Service Failure** $\rightarrow$ Return `UNAVAILABLE` (Do NOT assume in-stock).
- **Pricing Service Failure** $\rightarrow$ Fail Closed (Do NOT allow transaction with missing price).

---

## 🚀 8-Phase Development Roadmap

- **Phase 1**: Foundation (FastAPI service, PostgreSQL metadata DB, Pydantic DTOs).
- **Phase 2**: Listing Core (Resolvers, Listing Lifecycle state machine).
- **Phase 3**: View Engine (Card, Detail, Search View DTOs, FieldResolver).
- **Phase 4**: Template Engine (Template Registry, Admin Template APIs).
- **Phase 5**: Real-Time Commerce (Inventory, Pricing, Serviceability, ETA, Redis Cache).
- **Phase 6**: Trust & Eligibility (Seller verification, Action Engine, Server-side AuthZ).
- **Phase 7**: Search & Ranking (Deterministic multi-store ranking pipeline).
- **Phase 8**: Performance & Resilience (Parallel async `asyncio.gather`, Circuit Breakers).
