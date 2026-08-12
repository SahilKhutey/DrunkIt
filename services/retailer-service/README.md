# FACCP Retailer Service

Retailer Organizations, Store Network, State Excise License Tracking, Operating Hours, and Staff Management.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/retailer/organizations | Admin/Owner | Register retailer organization |
| GET | /api/v1/retailer/organizations/{id} | ✓ | Get organization details |
| POST | /api/v1/retailer/stores | Owner | Register store location |
| GET | /api/v1/retailer/stores/{id} | ✓ | Get store details |
| GET | /api/v1/retailer/organizations/{id}/stores | ✓ | List stores for organization |
| POST | /api/v1/retailer/stores/{id}/licenses | Admin/Owner | Add excise license |
| GET | /api/v1/retailer/stores/{id}/licenses | ✓ | List store licenses |
| POST | /api/v1/retailer/stores/{id}/staff | Manager | Assign staff member |
| GET | /api/v1/retailer/stores/{id}/staff | ✓ | List store staff |

## Database

Schema in `alembic/versions/0001_initial.py`. Tables:

- `retailer_organizations` — Legal business entity with GSTIN/PAN
- `stores` — Geo-coded physical store location
- `store_licenses` — State Excise License records with validity tracking
- `store_operating_hours` — Operating schedule per day
- `store_staff_assignments` — Assigned store staff members

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed retailer organizations and stores
uv run python -m app.scripts.seed_retailers

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```
