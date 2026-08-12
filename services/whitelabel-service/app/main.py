from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faccp_common.database import get_engine, get_session_factory
from faccp_common.kafka_client import EventProducer
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.api.routes import whitelabel_router
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
    producer = EventProducer(brokers=settings.kafka_brokers, client_id=settings.service_name)
    try:
        await producer.start()
        app.state.producer = producer
    except Exception:
        app.state.producer = None
    yield
    if getattr(app.state, "producer", None):
        await app.state.producer.stop()
    await engine.dispose()


app = FastAPI(title="FACCP White-Label Service", version=settings.service_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)
app.include_router(whitelabel_router, prefix="/api/v1")
