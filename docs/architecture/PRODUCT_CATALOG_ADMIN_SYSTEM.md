# FACCP Product Catalog Admin System Architecture

## Executive Overview
The Product Catalog Administration system enforces the core platform separation:

```
PRODUCT MASTER (admin owns)
       ↓
CATALOG LISTING (admin manages templates)
       ↓
RETAILER LISTING (retailer creates per store)
       ↓
CONSUMER VIEW (server-side projection only)
```

```
                    PRODUCT CATALOG ADMIN
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   Product Master       Categories           Brands
        │                   │                   │
        ├──────────────┬────┴──────┬────────────┘
        ▼              ▼           ▼
      SKU           Variants     Attributes
        │              │           │
        └──────────────┼───────────┘
                       ▼
                 Listing Engine
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         Retailer   Consumer     Search
          View       View         Index
```

---

## 🧙 The 10-Step Product Creation Wizard

Instead of overloading admins with 50+ raw fields, product creation follows a structured 10-step pipeline:

1. **Step 1: Product Identity**: Name, Brand, Manufacturer, Product Code, Description (`status: DRAFT`).
2. **Step 2: Classification**: Category, Subcategory, Product Type.
3. **Step 3: Dynamic Attributes**: Template-driven category fields (e.g. ABV, Volume, Packaging).
4. **Step 4: Media**: Primary image, gallery, asset upload, and metadata attachment.
5. **Step 5: Compliance Information**: Mandatory regulatory documents, excise classification, and jurisdiction restrictions.
6. **Step 6: SKU / Variants**: Multi-pack / size variant creation (`SKU-001` 650ml, `SKU-002` 330ml).
7. **Step 7: Preview**: Real-time rendering of the server-side Consumer Projection.
8. **Step 8: Validation**: Automated check across 7 gates (Schema, Required Fields, Compliance, Duplicates).
9. **Step 9: Review**: Final governance sign-off.
10. **Step 10: Publish**: Active publication and emission of `product.published` event.

---

## 🛡️ Dependency Checks & Soft Delete Protocol

The platform forbids hard-deleting products with active business linkages:

```
Remove Request → Active Listings? → (Yes: Handle Listings First) → Open Orders? → (Yes: Restrict Operation) → Historical Data? → Archive (Safest)
```

Product Lifecycle: `Draft` → `Pending Review` → `Approved` → `Active` → `Suspended` → `Archived`

---

## 📐 Low-Code Listing Template Engine

Admin-configurable Listing Templates define how retailers list products:
- **12 Supported Field Types**: `Text`, `Number`, `Boolean`, `Date`, `DateTime`, `Currency`, `Select`, `Multi-select`, `Image`, `Document`, `Reference`, `Computed`.
- **Template Versioning**: `v1.0` → `v1.1` → `v2.0` (`DRAFT` → `TESTING` → `APPROVED` → `ACTIVE` → `DEPRECATED`).

---

## 🔒 Admin vs Retailer Permission Matrix

| Capability | Admin Role | Retailer Role |
|---|---|---|
| **Create Product Master** | Allowed | Restricted |
| **Edit Product Master** | Allowed | Limited / Request |
| **Create Category & SKU** | Allowed | Limited |
| **Create Store Listing** | Allowed | Allowed |
| **Set Store Price & Inventory** | Policy-controlled | Allowed |
| **Global Product Suspension** | Allowed | Denied |
| **Remove From Own Store** | Allowed | Allowed |
