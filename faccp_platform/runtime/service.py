"""FastAPI service factory and baseline system endpoints."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, Callable

from fastapi import FastAPI

from .lifecycle import run_lifecycle_hooks


def create_service_app(
    *,
    name: str,
    version: str = "0.1.0",
    startup_hooks: list[Callable] | None = None,
    shutdown_hooks: list[Callable] | None = None,
) -> FastAPI:
    """Create and return a canonical FACCP microservice FastAPI application instance."""
    startup_hooks = startup_hooks or []
    shutdown_hooks = shutdown_hooks or []

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await run_lifecycle_hooks(startup_hooks)
        yield
        await run_lifecycle_hooks(shutdown_hooks)

    app = FastAPI(
        title=name,
        version=version,
        lifespan=lifespan,
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": name,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/ready", tags=["system"])
    async def ready() -> dict[str, str]:
        return {
            "status": "ready",
            "service": name,
            "version": version,
        }

    @app.get("/version", tags=["system"])
    async def version_info() -> dict[str, str]:
        return {
            "service": name,
            "version": version,
        }

    return app
