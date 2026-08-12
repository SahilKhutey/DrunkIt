# FACCP Analytics Service

Metrics Aggregation, Order Throughput, and Regulatory Excise Tax Report Snapshots.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/analytics/metrics | System | Record time-series metric aggregate |
| GET | /api/v1/analytics/metrics | Ops/Analytics | Query metrics |
| POST | /api/v1/analytics/snapshots | Auditor | Generate compliance report snapshot |
| GET | /api/v1/analytics/snapshots | Auditor | List historical report snapshots |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed metrics
uv run python -m app.scripts.seed_analytics

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8013 --reload
```
