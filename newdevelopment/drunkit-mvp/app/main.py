from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, consumer
from app.core.config import get_settings
from app.db import models  # noqa: F401 — ensures models are registered on Base
from app.db.session import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For MVP/dev only. Use Alembic migrations before this touches a
    # real Postgres database with real data in it.
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
