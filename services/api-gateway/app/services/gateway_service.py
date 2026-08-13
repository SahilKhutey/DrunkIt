"""API Gateway service router."""

from __future__ import annotations

import httpx

from app.config import get_settings
from app.schemas.gateway import GatewayHealthSummary, ServiceRouteInfo


class GatewayService:
    """Unified API Gateway manager & reverse proxy routing controller."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def get_routes(self) -> list[ServiceRouteInfo]:
        return [
            ServiceRouteInfo(service_name=name, target_url=url)
            for name, url in self.settings.services_map.items()
        ]

    async def get_health_summary(self) -> GatewayHealthSummary:
        routes = self.get_routes()
        return GatewayHealthSummary(
            total_services=len(routes),
            services=routes,
        )
