"""Compliance Service entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from faccp_platform.runtime.service import create_service_app
from .api.routes.eligibility import router as eligibility_router
from .api.routes.jurisdictions import router as jurisdiction_router
from .api.routes.policies import router as policy_router


def create_app() -> FastAPI:
    """Instantiate FACCP Compliance Service FastAPI application."""
    app = create_service_app(
        name="compliance-service",
        version="0.1.0",
    )
    app.include_router(eligibility_router)
    app.include_router(jurisdiction_router)
    app.include_router(policy_router)
    return app


app = create_app()
