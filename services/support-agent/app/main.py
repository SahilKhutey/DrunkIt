from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from faccp_common.database import get_db_session, get_engine, get_session_factory
from faccp_common.dto import SuccessResponse
from faccp_common.kafka_client import EventProducer
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.config import get_settings
from app.services.support_agent import SupportAgent

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


app = FastAPI(title="FACCP AI Support Agent Service", version=settings.service_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)


class SupportMessageRequest(BaseModel):
    conversation_id: str | None = None
    user_id: str
    content: str
    context: dict[str, Any] | None = None


@app.post("/api/v1/support/message", response_model=SuccessResponse[dict])
async def handle_support_message(payload: SupportMessageRequest) -> SuccessResponse[dict]:
    session_factory = app.state.db_session_factory
    producer = getattr(app.state, "producer", None)
    async for session in get_db_session(session_factory):
        agent = SupportAgent(db=session, producer=producer)
        res = await agent.handle_message(
            conversation_id=payload.conversation_id,
            user_id=payload.user_id,
            content=payload.content,
            context=payload.context,
        )
        return SuccessResponse(data=res)
