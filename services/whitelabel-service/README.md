# FACCP Whitelabel Service

Multi-Tenant Custom Branding, UI Themes, and Enterprise CNAME Domain Router.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/whitelabel/branding | Tenant Admin | Create/Update tenant UI branding config |
| GET | /api/v1/whitelabel/branding/{tenant_id} | Public | Fetch tenant branding colors & logo |
| POST | /api/v1/whitelabel/domains | Tenant Admin | Register custom CNAME domain binding |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed branding & domains
uv run python -m app.scripts.seed_whitelabel

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8015 --reload
```
