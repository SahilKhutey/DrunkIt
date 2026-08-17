# DrunkIt / FACCP — MVP

A working, end-to-end slice of the regulated alcohol quick-commerce platform:
**Eligibility Engine → Catalog/Listing Engine → Order → Delivery**, all in one
deployable FastAPI service. This is deliberately a fraction of the full FACCP
architecture — see "What's deferred" below for what was cut and why.

## ⚠️ Before this touches real users

`policies/jurisdictions.json` contains **placeholder data only**. Every Indian
state has its own excise rules on whether online alcohol delivery is legal at
all, and under what model. Do not enable a state (`allow_delivery: true`)
without a documented legal basis reviewed by qualified counsel, recorded in
that state's `legal_basis_ref`. The system fails closed by design — any state
not explicitly listed is treated as non-serviceable.

## Quick start

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

Then visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Architecture

```
Consumer API                          Admin API
     │                                     │
     ▼                                     ▼
Eligibility Engine  ──────┐      Retailer/Store/Product setup
  (age + jurisdiction)    │      Listing/Price/Inventory setup
     │                    │      Delivery ops (assign/transition/handoff)
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

- **Fail closed everywhere.** Missing price, missing inventory, or an
  unlisted jurisdiction all result in "not available," never a guess.
- **Server-side eligibility, every time.** `get_current_eligibility()` is
  re-evaluated on every checkout call — a consumer who was eligible an
  hour ago is re-checked against current state, not trusted from cache.
- **Price integrity.** `unit_price_paise` is snapshotted onto the order
  item at checkout time and never recomputed from "current price" later.
- **Controlled handoff.** `Delivery` can only become `DELIVERED` via
  `HANDOFF_VERIFICATION` — there is no code path that skips it.

## Repository layout

```
app/
  core/config.py          Settings (env-driven)
  db/
    models.py              SQLAlchemy models — Product/Retailer/Store/
                            Inventory/Price/Listing kept as separate tables
    session.py              Engine/session setup
  domain/
    eligibility/
      policy_store.py       Loads policies/jurisdictions.json (only reader)
      engine.py              Pure age+jurisdiction decision function
      service.py              Wires engine to DB + audit log
    listing/
      composer.py            Builds ConsumerListingView from separate sources
      service.py               Nearby-store query + composition
    order/service.py          Cart -> Order, server-side re-validation
    delivery/service.py       Delivery state machine + handoff gate
  api/
    consumer.py               Public-facing endpoints
    admin.py                  Retailer/store/product/listing/delivery ops
  schemas/schemas.py           Pydantic request/response models
  main.py                       FastAPI app wiring

policies/jurisdictions.json    Per-state legal rules (data, not code)
scripts/seed.py                  Demo data for local testing
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
- RBAC/authz on the admin API (currently assumes a trusted internal caller)

Each of these has a clear seam to plug into later — e.g. `mark_handoff_verified()`
in `delivery/service.py` is exactly where a real ID-scan/OTP provider replaces
the current pass-through boolean, without touching the state machine around it.

## Tests

```bash
pytest tests/ -v
```

Covers the eligibility engine's decision matrix, the listing fail-closed
behavior, and the order flow's stock/eligibility enforcement.
