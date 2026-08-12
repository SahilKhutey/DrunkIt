"""FastAPI dependencies for realtime service."""

from __future__ import annotations

from app.services.realtime_service import ConnectionManager, manager


def get_connection_manager() -> ConnectionManager:
    return manager
