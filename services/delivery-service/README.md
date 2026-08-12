# FACCP Delivery Service

Fulfillment Dispatch Missions, Live Driver Geolocation Tracking, and Doorstep OTP Proof-of-Delivery.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/delivery/missions | Order/Dispatch | Create delivery mission |
| GET | /api/v1/delivery/missions/{id} | ✓ | Get mission details |
| POST | /api/v1/delivery/missions/{id}/assign | Dispatch/Driver | Assign driver to mission |
| POST | /api/v1/delivery/missions/{id}/ping | Driver App | Record driver GPS location |
| POST | /api/v1/delivery/missions/{id}/complete | Driver App | Complete delivery via recipient OTP |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed delivery missions
uv run python -m app.scripts.seed_deliveries

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
```
