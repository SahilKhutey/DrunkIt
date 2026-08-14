"""Order service entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from faccp_platform.runtime.service import create_service_app
from .api.routes.carts import router as cart_router
from .api.routes.orders import router as order_router


def create_app() -> FastAPI:
    """Instantiate FACCP Order Service FastAPI application."""
    app = create_service_app(
        name="order-service",
        version="0.1.0",
    )
    app.include_router(cart_router)
    app.include_router(order_router)
    return app


app = create_app()
