# FACCP Audit Service

Cryptographic SHA256 Hash-Chained Immutable Audit Chain.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/audit/logs | System | Log event to cryptographic hash chain |
| GET | /api/v1/audit/logs | Auditor | List audit entries |
| GET | /api/v1/audit/verify-chain | Auditor | Verify SHA256 cryptographic chain integrity |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed audit entries
uv run python -m app.scripts.seed_audit

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```
