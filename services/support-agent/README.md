# FACCP AI Support Agent Service

Automated Customer Support, RAG Knowledge Base & Regulatory Permit Guidance Engine.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/support/message | Consumer | Handle conversational support inquiry |
| POST | /api/v1/support/tickets | Support/User | Create support ticket |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed knowledge docs & tickets
uv run python -m app.scripts.seed_support

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8016 --reload
```
