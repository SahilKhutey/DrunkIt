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
  success states, rust for failure states.
- **Type**: Fraunces (display, used with restraint) paired with Public Sans
  (body) and IBM Plex Mono (prices, timestamps, data — tabular figures).
- **Signature element**: the hexagonal `Seal` component (`src/components/Seal.tsx`),
  styled after an excise duty stamp pressed into a bottle label. Used
  consistently anywhere the platform is vouching for something — verified
  seller, age-verified account, or (in its rust tone) a failure/blocked
  state — instead of a generic checkmark or unrelated icon per case.

## Design system (`src/components/ui/`)

A small set of primitives every page is expected to use, rather than each
page reinventing its own button/input/toast:

| Component | Purpose |
|---|---|
| `Button` | 4 variants (primary/secondary/ghost/danger), loading state |
| `Input`, `Select` | Labeled form controls with a shared error-state treatment |
| `Badge` | Status pills (used for eligibility state on the Account page) |
| `Modal` | Dialog primitive (Escape-to-close, click-outside-to-close) |
| `SkeletonBlock`, `SkeletonCardGrid` | Loading placeholders |
| `EmptyState` | Consistent "nothing here" treatment |
| `ToastProvider` / `useToast()` | Centralized notifications — replaced the local `useState` + `setTimeout` toast pattern that used to be duplicated in HomePage and ProductDetailPage |

Import from the barrel: `import { Button, Input } from "../components/ui"`.

`src/components/InfoPage.tsx` is a page-level template (eyebrow/title/intro/
sections) rather than a UI primitive — it powers both `AboutPage` and
`ResponsibleDrinkingPage`, so a third informational page is a content change,
not a new layout.

## Pages

Every page reads from the real backend — there is no mocked or hardcoded
product data:

| Page | Route | Backend endpoints |
|---|---|---|
| Home | `/` | `GET /v1/listings` |
| Search | `/search` | `GET /v1/listings` (filtered client-side — see note below) |
| Product detail | `/product/:listingId` | `GET /v1/listings/{id}` |
| Login | `/login` | `POST /v1/auth/otp/request`, `POST /v1/auth/otp/verify` |
| Eligibility | `/eligibility` | `POST /v1/eligibility/verify` |
| Account | `/account` | `GET /v1/me` (via AuthContext) |
| Cart | `/cart` | client-side only (`CartContext`) until checkout |
| Checkout | `/checkout` | `POST /v1/orders` |
| Order tracking | `/orders/:orderId` | `GET /v1/orders/{id}`, `GET /v1/orders/{id}/delivery` (polled) |
| Order history | `/orders` | `GET /v1/orders` |
| About | `/about` | static content |
| Responsible drinking | `/responsible-drinking` | static content |
| 404 | any unmatched route | — |

An `ErrorBoundary` (`src/components/ErrorBoundary.tsx`) wraps the whole app
and shows a distinct "something broke" page for render-time errors, separate
from the 404 "nothing here" page.

## Known placeholders (see inline comments at each site)

- **Location**: a fixed lat/lng (Mumbai) stands in for real geolocation/address
  autocomplete — the backend's serviceability query already takes lat/lng,
  this just needs a real location source.
- **Search**: `SearchPage` filters the already-loaded listings client-side —
  there's no backend text-search endpoint yet. Fine at MVP catalog size;
  swap in a real `GET /v1/search/listings?q=` once the catalog is large
  enough that shipping the whole thing to the client stops being reasonable.
- **Delivery fee shown pre-checkout**: mirrors the backend's flat ₹25
  placeholder (`app/domain/order/service.py`) — replace both together when
  real delivery pricing lands.
- **OTP dev banner**: the login flow surfaces the raw OTP code on-screen
  outside production, because there's no SMS provider wired in yet. It
  disappears automatically once the backend's `environment` setting is
  `production` and a real provider is connected — see the backend's
  `app/domain/auth/service.py`.
- **About / Responsible Drinking copy**: descriptive marketing/informational
  text, not legal terms — actual Terms of Service / Privacy Policy content
  should come from counsel, not this codebase.

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
