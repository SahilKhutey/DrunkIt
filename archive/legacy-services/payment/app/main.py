"""Payment service entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from faccp_platform.runtime.service import create_service_app
from .api.routes.payments import router as payment_router
from .api.routes.webhooks import router as webhook_router


def create_app() -> FastAPI:
    """Instantiate FACCP Payment Service FastAPI application."""
    app = create_service_app(
        name="payment-service",
        version="0.1.0",
    )
    app.include_router(payment_router)
    app.include_router(webhook_router)
    return app


app = create_app()
