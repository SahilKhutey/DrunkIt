from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import admin, auth, consumer
from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.logging import RequestIdMiddleware, configure_logging
from app.db import models  # noqa: F401 — ensures models are registered on Base
from app.db.session import Base, engine

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all() is the dev/SQLite shortcut. In production (or any
    # environment using Alembic), set AUTO_CREATE_TABLES=false and let
    # `alembic upgrade head` (run in the Dockerfile CMD) own the schema.
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "DrunkIt/FACCP MVP — regulated alcohol quick-commerce API. "
        "Eligibility and jurisdiction checks are enforced server-side "
        "on every state-changing request; see app/domain/eligibility."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}


app.include_router(auth.router)
app.include_router(consumer.router)
app.include_router(admin.router)
