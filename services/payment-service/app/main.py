from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from faccp_common.database import close_engine, init_engine
from faccp_common.kafka_client import EventProducer
from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.telemetry import instrument_fastapi, setup_telemetry

from app.api.routes import payments_router
from app.config import get_settings
from app.db.base import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    init_engine(settings.database_url)
    engine = __import__("faccp_common.database", fromlist=["get_engine"]).get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        producer = EventProducer(bootstrap_servers=settings.kafka_bootstrap_servers, client_id=settings.kafka_client_id)
        await producer.start()
        app.state.event_producer = producer
    except Exception:
        app.state.event_producer = None

    if settings.enable_tracing:
        setup_telemetry(
            service_name=settings.service_name, service_version=settings.service_version,
            environment=settings.environment, otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )
    yield
    if getattr(app.state, "event_producer", None):
        await app.state.event_producer.stop()
    await close_engine()


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Payment Service", version=settings.service_version, lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(payments_router, prefix="/api/v1")
    app.mount("/metrics", make_asgi_app())

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "service": settings.service_name}

    if settings.enable_tracing:
        instrument_fastapi(app)
    return app


app = create_app()
