# FACCP Inventory Service

Real-time Store Inventory Balance, Stock Reservations with TTL, Atomic Deductions, and Immutable Audit Logs.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/inventory/stock | Manager | Update store SKU stock balance |
| GET | /api/v1/inventory/stock/{store_id}/{sku_id} | Public | Get stock balance |
| POST | /api/v1/inventory/reserve | Checkout | Reserve stock hold with TTL |
| POST | /api/v1/inventory/release | Checkout/Cancel | Release reservation back to stock |
| POST | /api/v1/inventory/deduct | Checkout | Fulfill reservation and deduct balance |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed inventory balances
uv run python -m app.scripts.seed_inventory

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```
