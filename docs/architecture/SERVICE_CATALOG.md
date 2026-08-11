# Service Catalog

This catalog describes the intended platform service boundaries. It should be treated as the starting point for the next integration pass.

| Service | Purpose | Current Notes |
| --- | --- | --- |
| identity-service | Accounts, auth, MFA, RBAC, identity security | Existing service foundation |
| consumer-service | Consumer profile and privacy-aware consumer data | Existing service foundation |
| retailer-service | Retailer organizations, stores, and licenses | Existing service foundation |
| catalog-service | Product and SKU catalog | Existing service foundation |
| inventory-service | Stock, reservations, and inventory movements | Existing service foundation |
| order-service | Cart, order orchestration, and state transitions | Existing service foundation |
| compliance-service | Jurisdiction policy evaluation | Existing service foundation |
| audit-service | Hash-chained audit events | Existing service foundation |
| risk-service | Risk scoring and ML fraud foundations | Existing service foundation |
| verification-service | Age and identity verification workflows | Existing service foundation |
| delivery-service | Driver assignment and delivery lifecycle | Existing service foundation |
| notification-service | Email, SMS, push, and transactional notifications | Existing service foundation |
| payment-service | Payment intents, capture, refunds, settlements, ledger | Existing service foundation |
| pricing-service | Price books, promotions, and pricing calculations | Existing service foundation |
| analytics-service | Event archiving and dashboard metrics | Existing service foundation |
| realtime-service | WebSocket and live event gateway | Existing service foundation |
| recommendation-service | Product recommendation engine | Existing service foundation |
| whitelabel-service | Tenants, themes, domains, and tenant configs | API added for Phase 4 |
| developer-portal | API marketplace, keys, subscriptions, quotas | Added in Phase 5 |
| cdp-service | Identity resolution, consent, segmentation, audiences | Added in Phase 6 |
| marketing-service | Campaign planning, A/B tests, journeys | Added in Phase 6 |
| api-gateway | REST reverse proxy gateway | Exists, needs full integration pass |

## Integration Rule

Every service should have:

- A unique service name and port.
- A Dockerfile.
- A `/health` endpoint.
- A database name when persistence is required.
- A gateway route when externally exposed.
- Unit tests for pure domain behavior.
- Integration tests for database-backed API behavior.
