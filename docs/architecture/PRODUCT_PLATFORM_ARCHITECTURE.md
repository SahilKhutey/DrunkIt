# FACCP Product Platform Architecture

## Executive Overview
The Product Platform establishes a non-negotiable architectural boundary separating **Truth** (`Product Master`) from **Presentation** (`User View Projections`).

```
Product Master    ≠    Retailer Listing    ≠    Inventory
      ≠                  ≠                  ≠
   Pricing          ≠   Compliance        ≠   Consumer View
```

```
                    PRODUCT PLATFORM
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       PRODUCT MASTER   RETAIL CATALOG   USER VIEW
             │             │             │
             ▼             ▼             ▼
        Product Data    Availability    Consumer UI
        Classification  Pricing         Search
        Compliance      Inventory       Details
        Media           Store           Recommendations
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    CATALOG API LAYER
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Consumer       Retailer       Admin
```

---

## 📊 The 16 Product Catalog Modules

1. **Product Master**: Canonical, authoritative product truth.
2. **Product Classification**: Category and subcategory taxonomy.
3. **Product Attributes**: Dynamic, catalog-governed attribute model.
4. **Product Media**: Object storage (S3) image and video assets.
5. **Product Compliance**: Regulatory metadata (jurisdiction eligibility, ABV limits).
6. **Brand Catalog**: Registered brand identities.
7. **Category Catalog**: Category hierarchy rules.
8. **SKU Catalog**: Sellable packaging units (e.g., 330ml, 650ml bottle).
9. **Variant Catalog**: Product variant mappings.
10. **Retailer Catalog**: Store listing associations.
11. **Store Availability**: Geofenced inventory state (`IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`).
12. **Pricing Engine Integration**: Decoupled pricing calculation.
13. **Inventory Service Integration**: Asynchronous stock availability checks.
14. **Search Index**: Denormalized search projections.
15. **Product Documents**: Specifications, licenses, quality certificates.
16. **Product Versioning**: Full change tracking history.

---

## 🔒 7 Field-Level Visibility Levels

| Level | Name | Target Audience | Example Fields |
|---|---|---|---|
| **0** | `Public` | Anonymous Users | Product Name, Brand, Description, Category |
| **1** | `Authenticated` | Logged-in Users | Store Availability |
| **2** | `Verified` | KYC-Verified Users | Special Commercial Offers |
| **3** | `Transaction Eligible` | Age-Verified Consumers | Transactional Purchase Controls |
| **4** | `Retailer` | Store Staff | Store Inventory, Wholesale Cost |
| **5** | `Administrative` | Platform Admins | Internal Compliance Notes, Regulatory Filings |
| **6** | `Internal/System` | Microservices Only | Internal Risk Signals, Anti-Fraud Flags |

---

## 🔄 Product Lifecycle States (9 States)

`DRAFT` → `SUBMITTED` → `VALIDATING` → `REVIEW` → `APPROVED` → `ACTIVE` → `SUSPENDED` → `DEPRECATED` → `ARCHIVED`

---

## 🎨 View Composer Engine (Projection Layer)

The consumer UI **NEVER** queries the internal `Product Master` directly. Requests route through the `View Composer` (`product-service`):

```
Frontend → API Gateway → View Composer (product-service) → 
  → Product Master (catalog-service)
  → Pricing Engine (pricing-service)
  → Inventory (inventory-service)
  → Policy (compliance-service)
  → User Context (identity-service)
  
= Composed Product View
```

Projections built by the View Composer:
- `ConsumerProductView`
- `RetailerProductView`
- `AdminProductView`
- `SearchProductView`
