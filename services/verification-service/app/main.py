from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faccp_common.database import close_engine, init_engine
from faccp_common.middleware import register_exception_handlers, register_middleware

from app.api.routes.verification import router as verification_router
from app.config import get_settings
from app.db.base import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    init_engine(settings.database_url)
    engine = __import__("faccp_common.database", fromlist=["get_engine"]).get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_engine()


app = FastAPI(title="FACCP Verification Service", version=settings.service_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)
app.include_router(verification_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.service_name}
