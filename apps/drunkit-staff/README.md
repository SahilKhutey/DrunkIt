# DrunkIt — Staff Console

React + TypeScript + Tailwind ops dashboard for the `/v1/admin/*` API in
`drunkit-mvp/`. Separate app from the consumer web app on purpose — separate
login, separate token, separate deployment — mirroring the backend's actual
identity boundary (`Session` vs `StaffSession`) rather than bolting admin
routes onto the public consumer bundle.

## Quick start

```bash
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your running backend
npm run dev
```

Requires the backend running with at least one staff account. The backend's
`python -m scripts.seed` creates two demo logins:

- `admin@demo.local` / `demo-admin-password-123` — `PLATFORM_ADMIN`
- `retailer@demo.local` / `demo-retailer-password-123` — `RETAILER_STAFF`,
  scoped to the demo retailer

For a real deployment, create the first admin with the backend's
`python -m scripts.create_admin` instead of relying on seed data.

## Two roles, one app

The UI adapts to whichever role is logged in rather than being two separate
builds:

- **`PLATFORM_ADMIN`** sees everything — Retailers (create, verify, issue
  retailer staff logins), the shared Products catalog, all Stores, and the
  Deliveries dispatch console.
- **`RETAILER_STAFF`** sees only Stores/Listings/Orders, scoped to their own
  retailer. The Retailers and Deliveries nav items don't even render for
  them (`Layout.tsx`'s `NAV_ITEMS.filter`), and `AdminOnlyRoute` blocks
  direct navigation to those routes too.

**This is a UX convenience, not the security boundary.** The backend
independently enforces every one of these restrictions via
`check_retailer_access()` regardless of what the frontend shows or hides —
verified with a live cross-retailer test against the running API, not just
trusted from the UI code (see the backend's `test_staff_auth.py` and the
"Staff authentication" section of its README).

## Pages

| Page | Route | Who sees it | Backend endpoints |
|---|---|---|---|
| Login | `/login` | everyone | `POST /v1/admin/auth/login` |
| Overview | `/` | everyone (content varies by role) | `GET /v1/admin/{retailers,stores,deliveries}` |
| Retailers | `/retailers` | `PLATFORM_ADMIN` | `GET/POST /v1/admin/retailers`, verify, staff account management |
| Stores | `/stores` | everyone (scoped) | `GET/POST /v1/admin/stores` |
| Listings | `/listings?store_id=` | everyone (scoped) | `GET/POST /v1/admin/listings`, `GET/POST /v1/admin/products` |
| Orders | `/orders?store_id=` | everyone (scoped) | `GET /v1/admin/orders` |
| Deliveries | `/deliveries` | `PLATFORM_ADMIN` | `GET /v1/admin/deliveries`, assign/transition/handoff |

The Listings page also has the platform catalog's "New product" action
(`PLATFORM_ADMIN` only) — products are shared platform-owned data, added
once and then listed independently at any store with that store's own price
and stock.

## Design

Shares the visual language of the consumer app (`drunkit-web/`) —
bottle-glass ink palette, brass accent, Fraunces/Public Sans/IBM Plex Mono —
for brand consistency, laid out as a sidebar console rather than a
storefront since the audience and task shape are completely different.

## Build

```bash
npm run build    # type-checks with tsc, then builds to dist/
npm run preview  # serve the production build locally
```
