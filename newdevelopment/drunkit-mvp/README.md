# DrunkIt / FACCP — MVP

A working, end-to-end slice of the regulated alcohol quick-commerce platform:
**Auth → Eligibility Engine → Catalog/Listing Engine → Order → Delivery**, all
in one deployable FastAPI service, plus a consumer web frontend in the
sibling `drunkit-web/` project. This is deliberately a fraction of the full
FACCP architecture — see "What's deferred" below for what was cut and why.

## ⚠️ Before this touches real users

`policies/jurisdictions.json` contains **placeholder data only**. Every Indian
state has its own excise rules on whether online alcohol delivery is legal at
all, and under what model. Do not enable a state (`allow_delivery: true`)
without a documented legal basis reviewed by qualified counsel, recorded in
that state's `legal_basis_ref`. The system fails closed by design — any state
not explicitly listed is treated as non-serviceable.

## Quick start (SQLite, no Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload
```

In another terminal, seed demo data (creates a demo retailer/store/products
and a temporary `DEMO_STATE` jurisdiction entry — remove that entry from
`policies/jurisdictions.json` before deploying anywhere real):

```bash
python -m scripts.seed
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs. Auth is
real phone+OTP — `POST /v1/auth/otp/request` returns `dev_otp` in the
response outside production (no SMS provider is wired in yet), then
`POST /v1/auth/otp/verify` with that code returns a bearer token for every
other consumer-scoped call.

## Quick start (Docker + Postgres)

```bash
cp .env.example .env   # values here aren't used by compose, but keep it for local tooling
docker compose up --build
```

This starts Postgres, waits for it to be healthy, runs `alembic upgrade head`,
then starts the API on `:8000` — see `Dockerfile`'s `CMD` and
`docker-compose.yml`. Seed it the same way as above, pointed at the
containerized DB:

```bash
DATABASE_URL=postgresql+psycopg2://drunkit:drunkit@localhost:5432/drunkit_mvp python -m scripts.seed
```

## Architecture

```
Consumer API                          Admin API
     │                                     │
     ▼                                     ▼
Auth (phone + OTP)              Retailer/Store/Product setup
  session token, not a           Listing/Price/Inventory setup
  client-supplied ID             Delivery ops (assign/transition/handoff)
     │
     ▼
Eligibility Engine  ──────┐
  (age + jurisdiction)    │
     │                    │
     ▼                    │
Listing Engine  ◄─────────┘
  (composes Product + Inventory
   + Price + Eligibility into a
   consumer-safe view — never
   copies those into one row)
     │
     ▼
Order Service
  (re-checks eligibility + inventory
   server-side at checkout, snapshots
   price so cart == checkout price)
     │
     ▼
Delivery Service
  (explicit state machine; cannot
   reach DELIVERED without passing
   through HANDOFF_VERIFICATION)
```

Key invariants enforced in code (not just UI):

- **Identity from the session, never the client.** Every consumer-scoped
  endpoint resolves the current consumer from the bearer token
  (`app/api/deps.py`) — a client can't act as another consumer by passing a
  different ID. See `tests/test_order_flow.py::test_client_cannot_impersonate_another_consumer_via_header`.
- **Fail closed everywhere.** Missing price, missing inventory, or an
  unlisted jurisdiction all result in "not available," never a guess.
- **Server-side eligibility, every time.** `get_current_eligibility()` is
  re-evaluated on every checkout call — a consumer who was eligible an
  hour ago is re-checked against current state, not trusted from cache.
- **Price integrity.** `unit_price_paise` is snapshotted onto the order
  item at checkout time and never recomputed from "current price" later.
- **Controlled handoff.** `Delivery` can only become `DELIVERED` via
  `HANDOFF_VERIFICATION` — there is no code path that skips it.

## Production hardening

Four things landed here beyond the initial MVP slice — each tested against
a real running server, not just unit tests:

### Database migrations (Alembic)

`migrations/` is wired to the app's own `Base.metadata` and reads
`DATABASE_URL` from the same settings the app uses — one source of truth,
no separate URL to keep in sync in `alembic.ini`.

```bash
alembic upgrade head              # apply all pending migrations
alembic revision --autogenerate -m "describe your change"   # after editing models
```

`Base.metadata.create_all()` (the dev convenience that used to run on every
startup) now only fires when `AUTO_CREATE_TABLES=true` **and** `DATABASE_URL`
is SQLite — see `main.py`'s `lifespan`. Anything else (Postgres, or a SQLite
file you actually care about) is expected to go through Alembic. This was
verified against a real local Postgres 16 instance: `alembic
revision --autogenerate` correctly detected all 15 tables from a clean
database, `alembic upgrade head` applied them, and the full
auth → eligibility → order → delivery flow was exercised against that
Postgres-backed API with `AUTO_CREATE_TABLES=false`.

### Postgres support

`app/db/session.py` adds `pool_pre_ping`, bounded pool size, and connection
recycling for any non-SQLite `DATABASE_URL` — SQLite's dev-only
`check_same_thread` connect arg is skipped for Postgres, and vice versa.

### Rate limiting

Two independent layers, because they defend against different things:

- **IP-based (slowapi)**: `5/minute` on `/v1/auth/otp/request`, `10/minute`
  on `/v1/auth/otp/verify`, `120/minute` default elsewhere. Stops one client
  hammering the API.
- **Per-phone OTP cooldown (`app/domain/auth/service.py`)**: a phone number
  can't have a new code requested within 45 seconds of its last one,
  regardless of which IP asks. This is the one that actually matters for
  OTP — SMS costs money per send, and without this a phone number could be
  harassed with texts from many different IPs, which the IP limiter alone
  wouldn't catch.

Tests disable rate limiting globally (`tests/conftest.py` sets
`RATE_LIMIT_ENABLED=false`) so the suite's rapid-fire requests don't trip
the same defense a real abusive client should hit — the cooldown itself is
still tested directly in `tests/test_hardening.py`.

### Structured logging

`app/core/logging.py` — JSON in production, readable console output in
dev, every log line inside a request auto-tagged with a correlation ID
(`X-Request-ID`, generated or echoed back from the caller) via structlog's
contextvars binding. Key domain events are logged at their source
(`otp_requested`, `order_created`, `order_rejected` with reason,
`delivery_transitioned`, `delivery_invalid_transition_blocked`,
`delivery_handoff_decision`) rather than only at the API boundary, so a log
line traces back to *why* something happened, not just that a request came
in. Never logged: OTP codes, session tokens, raw phone numbers (masked to
last 4 digits via `mask_phone()`), dates of birth.

## Repository layout

```
app/
  core/
    config.py                Settings (env-driven)
    logging.py                Structured logging + request-ID middleware
    limiter.py                 IP-based rate limiter (slowapi)
    time.py                     Shared UTC "now" helper
  db/
    models.py                SQLAlchemy models — Product/Retailer/Store/
                              Inventory/Price/Listing/Session/OTPChallenge
                              kept as separate tables
    session.py                 Engine/session setup (SQLite + Postgres)
  domain/
    auth/service.py           Phone+OTP, session issuance, per-phone cooldown
    eligibility/
      policy_store.py          Loads policies/jurisdictions.json (only reader)
      engine.py                 Pure age+jurisdiction decision function
      service.py                 Wires engine to DB + audit log
    listing/
      composer.py               Builds ConsumerListingView from separate sources
      service.py                  Nearby-store query + composition
    order/service.py             Cart -> Order, server-side re-validation
    delivery/service.py          Delivery state machine + handoff gate
  api/
    deps.py                   Auth dependencies (required / optional consumer)
    auth.py                    OTP request/verify endpoints
    consumer.py                 Public-facing endpoints (session-scoped)
    admin.py                     Retailer/store/product/listing/delivery ops
  schemas/schemas.py              Pydantic request/response models
  main.py                          FastAPI app wiring

migrations/                    Alembic migration environment + versions/
policies/jurisdictions.json    Per-state legal rules (data, not code)
scripts/seed.py                Demo data for local testing
Dockerfile, docker-compose.yml Postgres + API, migrations run on container start
```

## What's deferred (intentionally, from the original FACCP spec)

Cut for MVP because none of it earns its complexity before there are real
retailers and real orders:

- Listing template registry/field-resolver/visibility engine (one hardcoded
  card shape is enough for now)
- Driver app, GPS tracking, WebSocket live location, route optimization
- ML-based dispatch/ranking (the deterministic scoring approach from the
  original spec is the right *next* step, not this one)
- Kafka event bus (a request/response call is enough at this volume)
- Multi-region CRDTs, white-label tenancy, developer API marketplace, CDP,
  marketing automation
- Real identity/ID verification at the eligibility and handoff steps (this
  MVP takes a self-reported date of birth — swap in a real verification
  provider before this handles actual regulated transactions)
- RBAC/authz on the admin/retailer API (currently assumes a trusted internal
  caller — consumer-facing auth is real, admin-facing auth is not yet)
- Real SMS provider for OTP delivery (dev-mode returns the code directly —
  see the module docstring in `app/domain/auth/service.py` for the swap point)

Each of these has a clear seam to plug into later — e.g. `mark_handoff_verified()`
in `delivery/service.py` is exactly where a real ID-scan/OTP provider replaces
the current pass-through boolean, without touching the state machine around it.

## Tests

```bash
pytest tests/ -v
```

19 tests covering the eligibility engine's decision matrix, the listing
fail-closed behavior, the order flow's stock/eligibility enforcement, the
auth/impersonation boundary, and the rate-limiting/cooldown behavior. These
run against in-memory SQLite for speed; the migration path to Postgres is
verified separately (see "Production hardening" above) rather than in the
automated suite, which is the standard tradeoff — fast deterministic tests
for logic, a real database for proving the schema migrates correctly.

