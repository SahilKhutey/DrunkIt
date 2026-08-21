# @drunkit/types

Canonical frontend-facing domain and API contracts.

Initial contract families:

- Product
- ProductVariant
- SKU
- Brand
- Retailer
- RetailerLocation
- Inventory
- Availability
- ComplianceDecision
- Order
- EventEnvelope

The implementation should be generated/validated against the backend OpenAPI contract rather than maintaining incompatible hand-written models.
