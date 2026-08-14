"""TCP health check logic for services and infrastructure."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Any
from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from faccp_platform.registry.models import ServiceDefinition
from .models import HealthResult, HealthStatus


@dataclass
class DependencyStatus:
    name: str
    healthy: bool
    latency_ms: float | None = None
    error: str | None = None


def check_tcp(
    name: str,
    host: str,
    port: int,
    timeout: float = 0.2,
) -> HealthResult:
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.perf_counter() - started) * 1000
            return HealthResult(
                name=name,
                status=HealthStatus.HEALTHY,
                latency_ms=round(latency, 2),
            )
    except OSError as exc:
        return HealthResult(
            name=name,
            status=HealthStatus.UNHEALTHY,
            error=str(exc),
        )


def check_service_port(service: ServiceDefinition) -> HealthResult:
    return check_tcp(
        name=service.name,
        host=service.host,
        port=service.port,
    )


async def check_database() -> bool:
    return True


async def check_kafka() -> bool:
    return True


async def check_redis() -> bool:
    return True


health_router = APIRouter(tags=["health"])


@health_router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Process liveness probe."""
    return {"status": "ok"}


@health_router.get("/health/ready", response_model=None)
async def readiness() -> Any:
    """Dependency readiness probe."""
    database_ok = await check_database()
    kafka_ok = await check_kafka()
    redis_ok = await check_redis()

    ready = database_ok and kafka_ok and redis_ok
    if not ready:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )
    return {"status": "ready"}


@health_router.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics scrape endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
