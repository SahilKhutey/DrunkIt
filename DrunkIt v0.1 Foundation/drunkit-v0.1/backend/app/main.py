"""DrunkIt v0.1 — FastAPI Modular Monolith Application Entrypoint."""

import logging
from typing import Any

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1 import api_v1_router
from app.core.error_handlers import register_error_handlers
from app.core.middleware import register_middleware
from app.db.session import sync_engine
from app.settings import settings

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.app_env.upper() == "DEVELOPMENT" and "INFO" or "WARNING"),
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("drunkit.main")

app = FastAPI(
    title="DrunkIt API",
    version=settings.app_version,
    description="Alcohol Discovery & Retail Availability Platform (v0.1 Modular Monolith)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Middleware and Global Error Handlers
register_middleware(app)
register_error_handlers(app)

# Register API v1 Routers
app.include_router(api_v1_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness probe indicating the HTTP process is running."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, Any]:
    """Readiness probe evaluating database and infrastructure connectivity."""
    checks: dict[str, str] = {}
    is_ready = True

    # 1. Check database connectivity
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            checks["database"] = "ok"
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", exc)
        checks["database"] = "unavailable"
        is_ready = False

    return {
        "status": "ready" if is_ready else "degraded",
        "dependencies": checks,
    }


@app.get("/version", tags=["system"])
def version() -> dict[str, str]:
    """Application build and environment metadata."""
    return {
        "name": "drunkit-api",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
