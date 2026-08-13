# FACCP API Gateway Service

Unified Reverse Proxy, Rate Limiting & Service Mesh Routing Engine.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/v1/gateway/routes | Public | List downstream microservice routes |
| GET | /api/v1/gateway/health-all | Ops | Check health status across microservices |

## Development

```bash
# Start gateway
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
