"""Realtime service FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.telemetry import instrument_fastapi, setup_telemetry

from app.api.routes import realtime_router
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    setup_telemetry(
        service_name=settings.service_name,
        service_version=settings.service_version,
        environment=settings.environment,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="FACCP Realtime Service",
        version=settings.service_version,
        description="WebSockets Live Broadcast, Order Status & Delivery GPS Tracking Streams",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(realtime_router, prefix="/api/v1")
    app.mount("/metrics", make_asgi_app())

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": settings.service_name,
                "version": settings.service_version, "environment": settings.environment}

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        return {"status": "ready", "service": settings.service_name}

    instrument_fastapi(app)
    return app


app = create_app()
