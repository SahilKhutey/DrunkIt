# FACCP Order Service

Regulatory Order State Machine, Checkout Engine, Compliance Validation Integration.

## Regulatory State Machine

```
DRAFT -> COMPLIANCE_PENDING -> COMPLIANT -> PAYMENT_PENDING -> CONFIRMED -> DISPATCH_PENDING -> OUT_FOR_DELIVERY -> DELIVERED
  \              \                \                \               \                 \                  \
   +------------->+-------------->+--------------->+-------------->+---------------->+----------------->+----> CANCELLED
```

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/orders | Consumer | Create order draft |
| GET | /api/v1/orders/{id} | ✓ | Get order details |
| POST | /api/v1/orders/{id}/transition | Service/Admin | Transition order state |
| POST | /api/v1/orders/{id}/cancel | Consumer/System | Cancel order |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed orders
uv run python -m app.scripts.seed_orders

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```
