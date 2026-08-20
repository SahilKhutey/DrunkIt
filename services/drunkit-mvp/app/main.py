from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import admin, auth, consumer, staff_auth
from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.logging import RequestIdMiddleware, configure_logging, get_logger
from app.db import models  # noqa: F401 — ensures models are registered on Base
from app.db.session import Base, engine

settings = get_settings()
configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Table creation is only auto-run for local SQLite dev convenience.
    # Any real deployment (Postgres, or SQLite you actually care about)
    # should run `alembic upgrade head` explicitly instead — see
    # migrations/ and the README's "Database migrations" section.
    is_sqlite = settings.database_url.startswith("sqlite")
    if settings.auto_create_tables and is_sqlite:
        Base.metadata.create_all(bind=engine)
        log.info("startup_tables_auto_created", database_url=settings.database_url)
    else:
        log.info(
            "startup_skipped_auto_create",
            reason="not sqlite or auto_create_tables disabled",
            hint="run `alembic upgrade head`",
        )
    log.info("startup_complete", environment=settings.environment)
    yield
    log.info("shutdown_complete")


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
app.add_middleware(SlowAPIMiddleware)
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
app.include_router(staff_auth.router)
app.include_router(consumer.router)
app.include_router(admin.router)
