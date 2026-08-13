"""API Gateway schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ServiceRouteInfo(BaseModel):
    service_name: str
    target_url: str
    status: str = "CONFIGURED"


class GatewayHealthSummary(BaseModel):
    total_services: int
    services: list[ServiceRouteInfo]
