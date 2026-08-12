"""Recommendation service FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from faccp_common.database import close_engine, init_engine
from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.telemetry import instrument_fastapi, setup_telemetry

from app.api.routes import recommendation_router
from app.config import get_settings
from app.db.base import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    init_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        echo=settings.database_echo,
    )
    from faccp_common.database import get_engine
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    setup_telemetry(
        service_name=settings.service_name,
        service_version=settings.service_version,
        environment=settings.environment,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    )
    yield

    await close_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="FACCP Recommendation Service",
        version=settings.service_version,
        description="Personalized Recommendations & CDP Affinity Matching Engine",
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
    app.include_router(recommendation_router, prefix="/api/v1")
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
