"""FastAPI dependencies for API Gateway."""

from __future__ import annotations

from app.services.gateway_service import GatewayService


def get_gateway_service() -> GatewayService:
    return GatewayService()
