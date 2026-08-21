# DrunkIt v0.1 — Domain Model

## 1. Aggregate roots

The initial aggregate roots are:

- User
- Brand
- Product
- Retailer
- RetailerLocation
- Inventory
- Jurisdiction
- ComplianceRuleSet
- Cart
- Order
- AuditLog

## 2. Core relationships

```text
Brand
 └── Product
      └── ProductVariant
           └── SKU
                └── RetailerSKU
                     └── InventorySnapshot
                          └── Availability

Retailer
 └── RetailerLocation
      └── RetailerLicence

Jurisdiction
 └── ComplianceRuleSet
      └── ComplianceRule

User
 └── ConsumerProfile

User
 └── AuditLog
```

## 3. Identity

### User
- id
- email
- phone
- password_hash
- status
- created_at
- updated_at

### Role
- id
- code

### UserRole
- user_id
- role_id

### ConsumerProfile
- user_id
- date_of_birth_verified
- preferred_market
- preference data

## 4. Catalog

### Brand
- id
- name
- slug
- description
- country_id
- status

### Product
Canonical consumer-facing product.

- id
- brand_id
- category_id
- name
- slug
- description
- product_type
- region
- country_of_origin
- abv
- status

### ProductVariant
Commercial/package variation.

- id
- product_id
- volume_ml
- packaging_type
- package_count
- status

### SKU
Canonical sellable identifier.

- id
- variant_id
- canonical_code
- barcode
- status

### Category
Hierarchical product taxonomy.

- id
- parent_id
- name
- slug

### ProductAttribute
Flexible normalized attributes.

- id
- product_id
- key
- value

### TasteProfile
- product_id
- body
- sweetness
- smokiness
- bitterness
- fruitiness
- spiciness
- confidence

## 5. Retail

### Retailer
- id
- legal_name
- display_name
- status
- licence_status

### RetailerLocation
- id
- retailer_id
- name
- address
- city
- state_code
- postal_code
- country_code
- latitude
- longitude
- status

### RetailerLicence
- id
- retailer_id
- jurisdiction_id
- licence_number
- licence_type
- valid_from
- valid_to
- status
- evidence_uri

### RetailerSKU
Maps a retailer's local catalogue item to DrunkIt's canonical SKU.

- id
- retailer_location_id
- sku_id
- external_sku
- external_name
- status

## 6. Inventory and pricing

### InventorySnapshot
- id
- retailer_sku_id
- quantity
- availability_status
- captured_at
- source
- source_reference

### Price
- id
- retailer_sku_id
- amount_minor
- currency
- effective_from
- effective_to
- captured_at

The monetary value is stored in integer minor units.

## 7. Availability

Availability is a derived domain concept rather than an independently authoritative stock table.

Minimum output:

- sku_id
- retailer_location_id
- availability_status
- quantity_indicator
- price
- currency
- observed_at
- freshness_seconds

## 8. Compliance

### Jurisdiction
- id
- country_code
- state_code
- name
- timezone
- status

### ComplianceRuleSet
- id
- jurisdiction_id
- version
- effective_from
- effective_to
- status
- source_reference

### ComplianceRule
- id
- rule_set_id
- rule_type
- product_class
- licence_type
- age_requirement
- ordering_allowed
- delivery_allowed
- payment_allowed
- conditions_json
- source_reference

### ComplianceCheck
- id
- correlation_id
- consumer_id
- jurisdiction_id
- product_id
- retailer_id
- context_json
- requested_at

### ComplianceDecision
- id
- compliance_check_id
- decision
- reason_codes
- required_checks
- rule_set_version
- decided_at

## 9. Commerce foundation

Commerce entities exist in the model but transaction activation is controlled by market configuration.

### Cart
- id
- consumer_id
- jurisdiction_id
- status

### CartItem
- id
- cart_id
- sku_id
- retailer_location_id
- quantity
- price_snapshot

### Order
- id
- consumer_id
- retailer_location_id
- status
- currency
- subtotal_minor
- total_minor
- compliance_decision_id
- idempotency_key
- created_at

### OrderItem
- id
- order_id
- sku_id
- quantity
- unit_price_minor

## 10. Audit

### AuditLog
Append-only record.

- id
- actor_id
- action
- entity_type
- entity_id
- correlation_id
- metadata
- occurred_at

## 11. Data ownership rules

- Catalog owns canonical products.
- Retailer owns retailer identity and locations.
- Inventory owns retailer stock observations.
- Compliance owns regulatory rules and decisions.
- Commerce owns carts/orders.
- Audit owns immutable audit records.
- Analytics must not become the source of transactional truth.

## 12. Invariants

1. A SKU belongs to exactly one ProductVariant.
2. A ProductVariant belongs to exactly one Product.
3. A Product belongs to exactly one Brand.
4. Retailer SKU mappings must point to an existing canonical SKU.
5. Prices are never stored as floating point.
6. Compliance decisions reference an explicit rule-set version.
7. Expired retailer licences cannot produce an `ALLOW` compliance decision.
8. Inventory observations always have timestamps and sources.
9. Order creation is idempotent.
10. Audit records are append-only.
