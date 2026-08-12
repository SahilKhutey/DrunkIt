# FACCP Payment Service

Financial Ledger, Payment Intents, Gateway Captures, Refunds, and Double-Entry Accounting.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/payment/intents | Checkout | Create payment intent |
| GET | /api/v1/payment/intents/{id} | ✓ | Get payment intent details |
| POST | /api/v1/payment/intents/{id}/capture | Gateway/Checkout | Capture payment & post ledger |
| POST | /api/v1/payment/intents/{id}/refund | Admin/Support | Refund payment & post reversal ledger |
| GET | /api/v1/payment/ledger | Auditor/Admin | List double-entry ledger records |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed payments & ledger
uv run python -m app.scripts.seed_payments

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
```
