"""Consumer service entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from faccp_platform.runtime.service import create_service_app
from .api.routes.consumers import router as consumer_router
from .api.routes.profiles import router as profile_router
from .api.routes.verification import router as verification_router


def create_app() -> FastAPI:
    """Instantiate FACCP Consumer Service FastAPI application."""
    app = create_service_app(
        name="consumer-service",
        version="0.1.0",
    )
    app.include_router(consumer_router)
    app.include_router(profile_router)
    app.include_router(verification_router)
    return app


app = create_app()
