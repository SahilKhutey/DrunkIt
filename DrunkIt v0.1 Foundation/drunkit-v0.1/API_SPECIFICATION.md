# DrunkIt v0.1 — API Specification

Base path:

`/api/v1`

## Conventions

- JSON request/response bodies.
- UUID identifiers.
- ISO-8601 timestamps.
- Monetary amounts use integer minor units.
- Pagination uses `limit` + `cursor`.
- Errors use a consistent envelope.

## Error envelope

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Product was not found.",
    "request_id": "uuid",
    "details": {}
  }
}
```

## Health

### GET /health
Liveness.

### GET /ready
Dependency readiness.

### GET /version
Application version and build metadata.

## Authentication

### POST /auth/register
Creates a user.

### POST /auth/login
Authenticates a user.

### POST /auth/logout
Terminates the current session.

### GET /auth/me
Returns the authenticated principal.

## Products

### GET /products
Query parameters:

- `q`
- `category`
- `brand_id`
- `min_price`
- `max_price`
- `min_abv`
- `max_abv`
- `state_code`
- `city`
- `limit`
- `cursor`

### GET /products/{product_id}

Returns canonical product information.

### GET /products/{product_id}/availability

Returns eligible retailer availability.

## Brands

### GET /brands
Lists brands.

### GET /brands/{brand_id}
Returns a brand profile.

### GET /brands/{brand_id}/products
Returns the brand catalogue.

## Retailers

### GET /retailers
Lists discoverable retailers.

### GET /retailers/{retailer_id}
Returns retailer information.

### GET /retailers/{retailer_id}/locations
Lists retailer locations.

### POST /retailers
Retailer onboarding endpoint.

## Inventory

### POST /retailers/{retailer_id}/inventory
Creates/updates inventory observations.

### GET /retailers/{retailer_id}/inventory
Returns retailer inventory.

### POST /retailers/{retailer_id}/inventory/import
CSV/import boundary for later implementation.

## Discovery

### GET /search
Initial PostgreSQL full-text discovery endpoint.

### GET /discovery/home
Returns curated discovery modules.

### GET /recommendations
Returns V1 rule-based recommendations.

## Compliance

### POST /compliance/check

Request:

```json
{
  "consumer_id": "uuid",
  "location": {
    "country_code": "IN",
    "state_code": "XX"
  },
  "product_id": "uuid",
  "retailer_id": "uuid",
  "context": "AVAILABILITY"
}
```

Response:

```json
{
  "decision": "ALLOW",
  "reason_codes": [],
  "required_checks": [],
  "rule_set_version": "jurisdiction-version",
  "expires_at": "2026-08-21T10:00:00Z"
}
```

## Cart

### GET /cart
Returns the active cart.

### POST /cart/items
Adds an item after server-side validation.

### PATCH /cart/items/{item_id}
Updates quantity.

### DELETE /cart/items/{item_id}
Removes an item.

## Orders

Commerce endpoints are feature-gated by jurisdiction.

### POST /orders
Creates an order using an idempotency key.

### GET /orders/{order_id}
Returns order state.

### GET /orders
Lists consumer orders.

## Events

Internal event records are not exposed as a public API in v0.1.

## RBAC

| Endpoint group | Consumer | Retailer | Brand | Admin |
|---|---:|---:|---:|---:|
| Products read | ✓ | ✓ | ✓ | ✓ |
| Retailer inventory | — | Own | — | ✓ |
| Retailer onboarding | — | ✓ | — | ✓ |
| Compliance rules | — | — | — | ✓ |
| Audit logs | — | Limited | Limited | ✓ |
| Orders | Own | Assigned | — | ✓ |

## API design rules

1. No unversioned public endpoints.
2. Never trust client-side compliance state.
3. Never trust client-provided price totals.
4. Every mutating request validates authorization.
5. Mutating commands support idempotency where duplicate execution is possible.
6. API schemas are generated/validated from the canonical contract.
