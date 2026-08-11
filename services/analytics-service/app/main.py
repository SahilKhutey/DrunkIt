from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import close_engine, get_db, init_engine
from faccp_common.dto import APIResponse
from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.telemetry import instrument_fastapi, setup_telemetry

from app.config import get_settings
from app.db.base import Base
from app.services.analytics_service import AnalyticsService

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    init_engine(settings.database_url)
    engine = __import__("faccp_common.database", fromlist=["get_engine"]).get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.enable_tracing:
        setup_telemetry(
            service_name=settings.service_name, service_version=settings.service_version,
            environment=settings.environment, otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )
    yield
    await close_engine()


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Analytics Service", version=settings.service_version, lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    register_middleware(app)
    register_exception_handlers(app)
    app.mount("/metrics", make_asgi_app())

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/api/v1/analytics/dashboard")
    async def get_dashboard(db: AsyncSession = Depends(get_db)) -> APIResponse[dict]:
        service = AnalyticsService(db)
        data = await service.get_dashboard_summary()
        return APIResponse(data=data)

    if settings.enable_tracing:
        instrument_fastapi(app)
    return app


app = create_app()
