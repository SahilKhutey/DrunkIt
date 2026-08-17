# DrunkIt — Consumer Web App

React + TypeScript + Tailwind consumer frontend for the DrunkIt/FACCP MVP
backend. Talks to the FastAPI service in `drunkit-mvp/`.

## Quick start

```bash
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your running backend
npm run dev
```

Requires the backend running (see the backend README) — this app has no
mock data of its own; every product, price, and order comes from the API.

## Design direction

This is a regulated, trust-first category — not a playful grocery app — so
the visual language deliberately avoids both generic quick-commerce
brightness and the generic AI-default looks (cream+terracotta, near-black
+neon):

- **Palette**: bottle-glass ink green as the base surface, brass/excise-seal
  gold as the primary accent, aged-copper for price emphasis, muted sage for
  success states.
- **Type**: Fraunces (display, used with restraint) paired with Public Sans
  (body) and IBM Plex Mono (prices, timestamps, data — tabular figures).
- **Signature element**: the hexagonal `Seal` component (`src/components/Seal.tsx`),
  styled after an excise duty stamp pressed into a bottle label. Used
  consistently anywhere the platform is vouching for something — verified
  seller, verified listing — instead of a generic checkmark.

## What talks to what

Every page reads from the real backend — there is no mocked or hardcoded
product data:

| Page | Backend endpoints |
|---|---|
| Login | `POST /v1/auth/otp/request`, `POST /v1/auth/otp/verify` |
| Eligibility | `POST /v1/eligibility/verify` |
| Home / product grid | `GET /v1/listings` |
| Product detail | `GET /v1/listings/{id}` |
| Cart | client-side only (`CartContext`) until checkout |
| Checkout | `POST /v1/orders` |
| Order tracking | `GET /v1/orders/{id}`, `GET /v1/orders/{id}/delivery` (polled) |
| Order history | `GET /v1/orders` |

## Known placeholders (see inline comments at each site)

- **Location**: a fixed lat/lng (Mumbai) stands in for real geolocation/address
  autocomplete — the backend's serviceability query already takes lat/lng,
  this just needs a real location source.
- **Delivery fee shown pre-checkout**: mirrors the backend's flat ₹25
  placeholder (`app/domain/order/service.py`) — replace both together when
  real delivery pricing lands.
- **OTP dev banner**: the login flow surfaces the raw OTP code on-screen
  outside production, because there's no SMS provider wired in yet. It
  disappears automatically once the backend's `environment` setting is
  `production` and a real provider is connected — see the backend's
  `app/domain/auth/service.py`.

## Known dependency advisories

`npm audit` will show a moderate-severity esbuild/Vite advisory
(GHSA-67mh-4wv8-2f99) affecting the **dev server only** — it allows a
malicious website to make requests to `vite dev` if it's exposed to an
untrusted network. It does not affect the production build output. Run
`npm audit fix --force` to take the Vite 8 major upgrade if you want it
resolved before this dev server is ever exposed beyond localhost.

## Build

```bash
npm run build    # type-checks with tsc, then builds to dist/
npm run preview  # serve the production build locally
```
