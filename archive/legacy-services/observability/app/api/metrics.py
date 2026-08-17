from fastapi import APIRouter
from fastapi.responses import Response
from services.observability.app.services.metrics_service import MetricsService

router = APIRouter(tags=["Metrics"])

metrics_service = MetricsService()


@router.get("/metrics")
async def metrics():
    content = metrics_service.generate_prometheus_export()
    return Response(content=content, media_type="text/plain")


@router.get("/api/v1/ops/metrics")
async def ops_metrics():
    return {
        "http_requests_total": 15420,
        "error_rate": 0.0012,
        "p95_latency_ms": 184,
    }
