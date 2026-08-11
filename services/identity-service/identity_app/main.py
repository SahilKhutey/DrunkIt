from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from faccp_common.database import close_engine, init_engine
from faccp_common.logging import configure_logging, get_logger
from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.telemetry import instrument_fastapi, setup_telemetry
from identity_app.api.routes import auth
from identity_app.config import get_settings

settings = get_settings()

configure_logging(
    service_name=settings.service_name,
    service_version=settings.service_version,
    level=settings.log_level,
    environment=settings.environment,
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting identity-service...", port=settings.port)
    init_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.database_echo,
    )
    if settings.enable_tracing:
        setup_telemetry(
            service_name=settings.service_name,
            service_version=settings.service_version,
            environment=settings.environment,
            otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )
    yield
    logger.info("Shutting down identity-service...")
    await close_engine()


app = FastAPI(
    title="FACCP Identity Service",
    version=settings.service_version,
    description="Identity Vault, Auth, JWT issuance, and RBAC management.",
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

if settings.enable_tracing:
    instrument_fastapi(app)

app.include_router(auth.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": settings.service_name, "version": settings.service_version}
