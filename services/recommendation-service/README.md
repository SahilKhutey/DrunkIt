# FACCP Recommendation Service

Personalized Product Discovery, CDP Preference Profiles, and Affinity Score Engine.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/recommendations/profiles | System/Consumer | Create/Update preference profile |
| POST | /api/v1/recommendations/affinities | System/ML | Record product co-occurrence affinity |
| GET | /api/v1/recommendations/personalized/{consumer_id} | Consumer | Fetch personalized recommendations |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed recommendations
uv run python -m app.scripts.seed_recommendations

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8014 --reload
```
