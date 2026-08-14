"""FastAPI Prometheus metrics middleware."""

from __future__ import annotations

import time
from typing import Any
from fastapi import Request, Response
from .metrics import HTTP_LATENCY, HTTP_REQUESTS


async def metrics_middleware(request: Request, call_next: Any) -> Response:
    """Middleware capturing request counts and duration metrics for Prometheus."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    service_name = getattr(request.app, "title", "faccp-service")
    route = request.url.path

    try:
        HTTP_REQUESTS.labels(
            service=service_name,
            method=request.method,
            route=route,
            status=response.status_code,
        ).inc()

        HTTP_LATENCY.labels(
            service=service_name,
            method=request.method,
            route=route,
        ).observe(duration)
    except Exception:
        pass

    return response
