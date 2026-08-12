# FACCP Consumer Listing Engine Architecture

## Executive Overview
The Consumer Listing Engine v1 embodies the **"Quick Commerce + Trust Commerce"** model. It combines the speed and simplicity of quick-commerce discovery (Blinkit, Zepto, Instamart) with architectural trust verification (verified seller, verified listing, transparent pricing, real-time availability, and eligibility controls).

```
QUICK COMMERCE              FACCP
────────────────────────    ────────────────────────
Fast discovery              Fast discovery
                           +
                           Accurate product identity
                           +
                           Verified seller
                           +
                           Verified listing
                           +
                           Transparent pricing
                           +
                           Real-time availability
                           +
                           Eligibility controls
                           +
                           Auditable transaction
```

---

## 🏛️ Composed Listing Object (`ConsumerListingView`)

The backend composes the listing object server-side per user context:

```json
{
  "product": {
    "id": "P001",
    "name": "Kingfisher Premium Lager",
    "brand": "Kingfisher",
    "variant": "Standard",
    "pack_size": "650 ml"
  },
  "commercial": {
    "mrp": 220,
    "selling_price": 200,
    "discount": 20
  },
  "availability": {
    "status": "IN_STOCK"
  },
  "fulfilment": {
    "store": "Mumbai Central Store #42",
    "eta": "20-30 min"
  },
  "trust": {
    "seller_verified": true,
    "listing_verified": true,
    "license_status": "FL3_VERIFIED"
  },
  "actions": {
    "view": true,
    "add_to_cart": true
  }
}
```

---

## 💰 Price Integrity Engine (`PriceIntegrityValidator`)

Strict architectural rule:
```
DISPLAYED PRODUCT PAGE PRICE = CART PRICE = CHECKOUT PRICE
```
- No hidden fees added at checkout.
- Displayed MRP must strictly equal Actual MRP from authoritative catalog.
- Client UIs display backend-calculated prices and **never** compute or modify prices independently.

---

## 📐 3 Listing Template Types

1. **Template A: Compact Card (Quick-Commerce Style)**: Image + Name + Pack Size + Price + Availability + Add CTA.
2. **Template B: Rich Card (Standard E-Commerce)**: Image + Brand + Name + Pack Size + Price + MRP + Discount + Delivery ETA + Trust Badge.
3. **Template C: Regulated Card (FACCP-Specific)**: Image + Brand + Name + Pack Size + Price + Availability + Verified Seller Badge + Eligibility State + View Action.

---

## ⚙️ The 18 Consumer Engine Modules

1. `ProductCard`: Fundamental display component.
2. `ProductGrid`: Responsive layout grid system.
3. `SearchResultCard`: Search-optimized lightweight display.
4. `CategoryListing`: Filterable category page renderer.
5. `ProductDetail`: Full progressive disclosure detail page.
6. `PriceDisplay`: Tax-included price and discount component.
7. `AvailabilityBadge`: Real-time stock status indicator (`IN_STOCK`, `LOW_STOCK`, `UNAVAILABLE`).
8. `SellerVerificationBadge`: Trust & license verification badge.
9. `EligibilityBanner`: Contextual user eligibility status banner.
10. `StoreAvailability`: Store-level geofenced stock locator.
11. `DeliveryETA`: Serviceability & estimated delivery time.
12. `RecommendationCarousel`: Policy-governed related products.
13. `ListingTemplateRenderer`: Config-driven template renderer.
14. `ResponsiveLayout`: Mobile, Tablet, and Desktop breakpoints.
15. `LoadingSkeletonStates`: Skeleton loader feedback.
16. `EmptyErrorStates`: Accessible empty and error boundaries.
17. `AccessibilityLayer`: WCAG 2.2 AA compliant ARIA & keyboard hooks.
18. `AnalyticsEvents`: Privacy-safe telemetry emitters.
