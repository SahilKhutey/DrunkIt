# FACCP Web UI / Visual Development Guide Architecture

## Executive Overview
The Web UI is a multi-portal, role-aware interface system that mirrors the backend's domain separation. Four distinct portals (Consumer, Retailer, Admin, Developer) share one design language system while optimizing for their respective user groups, information densities, and interaction patterns.

```
                    WEB PLATFORM
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   CONSUMER WEB     RETAILER WEB      ADMIN WEB
   (Simple)         (Operational)     (Information-dense)
   (Trustworthy)    (Efficient)       (Controlled)
        │                │                │
        └────────────────┼────────────────┘
                         │
                    DESIGN SYSTEM
                    (Shared Foundation)
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Tokens    Components   Patterns
              │          │          │
              └──────────┼──────────┘
                         ▼
                   UI PLATFORM
              (The 4 Portals + APIs + WebSocket + Events)
```

---

## 🎯 The 6 UI Architecture Principles

1. **P1 — Role Separation**: Separate information architectures and visual weights for Consumer (Simple), Retailer (Operational), Admin (Governance), and Developer (Documentation).
2. **P2 — Progressive Disclosure**: Reveal detail on demand (Basic → Expanded → Section → Dedicated Admin View).
3. **P3 — Action Clarity**: Communicate WHAT, WHY, CONSEQUENCE, REQUIRED INPUT, and RESULT for every action.
4. **P4 — Safety First**: No dark patterns, no fake urgency timers, no deceptive language.
5. **P5 — Trust Visibility**: Clear visibility into seller identity, real-time availability, eligibility status, and delivery windows.
6. **P6 — Consistency**: Identical component behaviors and confirmation patterns across all portals.

---

## 📂 The 4 Role-Aware Portals

- **Consumer Portal (`consumer-web/`)**: Light, spacious, calm visual weight. Guided checkout flow (Cart → Address → Eligibility → Delivery → Payment → Review → Confirmation).
- **Retailer Portal (`retailer-web/`)**: Operational efficiency, high data density, real-time status indicators, data tables with bulk actions.
- **Admin Portal (`admin-web/`)**: Information-dense dashboards, drill-down navigation, policy management, visible audit trails.
- **Developer Portal (`developer-web/`)**: Technical reference, OpenAPI explorers, schema viewers, SDK downloads, interactive sandbox.

---

## 🎨 Design Tokens & Component Hierarchy

### 9 Token Categories
- `Colors` (Primary, Neutral, Semantic, Status)
- `Typography` (Display, H1..H3, Body, Mono)
- `Spacing` (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80)
- `Radius` (0, 4, 8, 12, 16, 24, 9999)
- `Shadows` (Elevation levels 0..4)
- `Borders`
- `Breakpoints` (sm, md, lg, xl, 2xl)
- `Motion` (Durations, Easings)
- `Z-Index` (Layers scale)

### 6 Component Layers
`Tokens` → `Primitives` (Button, Input, Badge, Tooltip) → `Components` (ProductCard, StatusBadge, DataTable) → `Patterns` (ProductPage, CheckoutFlow, DashboardLayout) → `Sections` → `Pages` → `Applications`

---

## 🏷️ 7 Status Visual Treatments

| Status | Icon / Indicator | Color Treatment | Text Label |
|---|---|---|---|
| **Verified** | Checkmark | Green | `Verified` |
| **Pending** | Clock | Yellow | `Pending` |
| **Requires Action** | Alert | Orange | `Action Required` |
| **Restricted** | Lock | Red | `Restricted` |
| **Unavailable** | Dash | Gray | `Unavailable` |
| **Suspended** | Pause | Red | `Suspended` |
| **Expired** | X | Gray | `Expired` |

---

## ♿ Accessibility Baseline (WCAG 2.2 AA)

- Full keyboard navigation and visible focus indicators.
- 4.5:1 minimum contrast ratio for body text.
- Screen-reader labels (`aria-label`, `aria-describedby`, `aria-live`).
- Touch-friendly targets (minimum 44x44px).
- Reduced-motion support (`prefers-reduced-motion`).
