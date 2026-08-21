# DrunkIt — Regulatory Engine & Compliance Decision API Specification

## Executive Overview

The **DrunkIt Compliance Engine (FACCP Core)** is a pure, deterministic, fail-closed policy engine that evaluates whether an alcohol search, discovery, reservation, or purchase transaction is lawful under the applicable jurisdiction's legal framework.

---

## 1. Compliance Decision API Specification

### Endpoint: `POST /api/v1/compliance/check`

Evaluates a transaction or discovery intent against active jurisdiction rulesets.

#### 1.1 Request Payload Schema (JSON)
```json
{
  "consumer": {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "verified_age": 24,
    "kyc_verified": true,
    "residence_state": "IN-WB"
  },
  "location": {
    "latitude": 22.572645,
    "longitude": 88.363892,
    "state_code": "IN-WB",
    "pincode": "700001"
  },
  "retailer": {
    "retailer_location_id": "7ca85f64-5717-4562-b3fc-2c963f66afa1",
    "license_number": "WB/EX/FL/2024/8892",
    "license_category": "FL-OFF",
    "license_valid_to": "2027-03-31"
  },
  "items": [
    {
      "sku_id": "SKU_JWB_750",
      "product_name": "Johnnie Walker Black Label 12YO",
      "category": "SPIRITS",
      "volume_ml": 750,
      "abv_percentage": 40.0,
      "quantity": 1,
      "unit_price_mrp": 3200.00
    }
  ],
  "order_mode": "HOME_DELIVERY",
  "request_timestamp": "2026-08-21T18:30:00+05:30"
}
```

#### 1.2 Success Response (ALLOW)
```json
{
  "decision": "ALLOW",
  "decision_id": "dec_98f12a34-5717-4562-b3fc-2c963f66afa9",
  "jurisdiction_code": "IN-WB",
  "rule_version": "IN-WB-2026-08-v1",
  "evaluated_at": "2026-08-21T13:00:01.124Z",
  "reason_codes": [],
  "passed_checks": [
    "STATUTORY_AGE_CHECK",
    "DRY_DAY_CALENDAR_CHECK",
    "OPERATING_HOURS_CHECK",
    "RETAILER_LICENCE_VALIDITY",
    "POSSESSION_LIMIT_CHECK",
    "DELIVERY_RADIUS_BOUNDARY_CHECK"
  ],
  "restrictions": {
    "max_allowed_delivery_time": "2026-08-21T22:00:00+05:30",
    "recipient_verification_required": "OTP_AND_PHYSICAL_ID"
  },
  "hash_signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

#### 1.3 Rejected Response (DENY)
```json
{
  "decision": "DENY",
  "decision_id": "dec_98f12a34-5717-4562-b3fc-2c963f66afb0",
  "jurisdiction_code": "IN-MH",
  "rule_version": "IN-MH-2026-08-v1",
  "evaluated_at": "2026-08-21T13:00:01.124Z",
  "reason_codes": [
    "AGE_BELOW_STATUTORY_MINIMUM_FOR_SPIRITS",
    "DIGITAL_DELIVERY_NOT_PERMITTED_IN_JURISDICTION"
  ],
  "remediation": {
    "fallback_mode": "ASSISTED_COMMERCE_STORE_LOCATOR",
    "minimum_age_required": 25,
    "nearest_licensed_stores": [
      {
        "store_name": "Living Liquidz Bandra",
        "distance_km": 1.2,
        "directions_url": "https://maps.drunkit.in/store/7ca85f64"
      }
    ]
  },
  "hash_signature": "d41d8cd98f00b204e9800998ecf8427e00000000000000000000000000000000"
}
```

---

## 2. Policy-as-Code Data Structure (YAML)

State policies are stored as structured declarative data in `policies/jurisdictions/`:

```yaml
jurisdiction:
  code: "IN-WB"
  name: "West Bengal"
  country: "IND"
  policy_version: "IN-WB-2026-08-v1"
  effective_from: "2026-08-01T00:00:00Z"
  effective_to: "2027-03-31T23:59:59Z"

statutory_rules:
  minimum_drinking_age:
    spirits: 21
    beer: 21
    wine: 21
  delivery_allowed: true
  assisted_commerce_allowed: true
  max_possession_volume_ml: 9000
  retail_operating_hours:
    start_time: "10:00"
    end_time: "22:00"
    timezone: "Asia/Kolkata"

dry_days:
  - date: "2026-10-02"
    name: "Gandhi Jayanti"
    scope: "ALL_OUTLETS"
  - date: "2026-08-15"
    name: "Independence Day"
    scope: "ALL_OUTLETS"
  - date: "2026-01-26"
    name: "Republic Day"
    scope: "ALL_OUTLETS"

license_requirements:
  valid_categories:
    - "FL-OFF"
    - "CS-OFF"
  require_platform_admin_verification: true

audit:
  require_merkle_chaining: true
  hash_algorithm: "SHA-256"
```
