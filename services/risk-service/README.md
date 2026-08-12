# FACCP Risk Service

Real-time Fraud Detection, Velocity Threshold & Risk Evaluation Engine.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/risk/evaluate | System/Order | Evaluate risk score for entity |
| POST | /api/v1/risk/rules | Risk Admin | Create fraud pattern rule |
| GET | /api/v1/risk/flagged | Risk Admin | List REVIEW or REJECT flagged evaluations |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed fraud rules
uv run python -m app.scripts.seed_risk

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
```
