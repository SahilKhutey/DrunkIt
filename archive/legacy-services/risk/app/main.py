"""Risk engine service entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from faccp_platform.runtime.service import create_service_app
from .api.routes.risk import router as risk_router


def create_app() -> FastAPI:
    """Instantiate FACCP Risk Service FastAPI application."""
    app = create_service_app(
        name="risk-service",
        version="0.1.0",
    )
    app.include_router(risk_router)
    return app


app = create_app()
