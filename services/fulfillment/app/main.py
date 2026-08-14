"""Fulfillment Service FastAPI application entrypoint."""

from __future__ import annotations

from faccp_platform.runtime import create_service_app
from .api.routes import delivery_router, fulfillment_router

app = create_service_app(
    service_name="fulfillment-service",
    version="1.0.0",
    description="Fulfillment and Delivery Execution Kernel",
)

app.include_router(fulfillment_router)
app.include_router(delivery_router)
