"""API Gateway service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings
from faccp_common.registry import load_registry


class GatewayServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-gateway"
    port: int = 8000

    @property
    def services_map(self) -> dict[str, str]:
        try:
            reg = load_registry()
            return reg.get_gateway_routes()
        except Exception:
            return {
                "identity": "http://localhost:8001",
                "consumer": "http://localhost:8002",
                "retailer": "http://localhost:8003",
                "catalog": "http://localhost:8004",
                "inventory": "http://localhost:8005",
                "order": "http://localhost:8006",
                "compliance": "http://localhost:8007",
                "payment": "http://localhost:8008",
                "delivery": "http://localhost:8009",
                "audit": "http://localhost:8010",
                "risk": "http://localhost:8011",
                "realtime": "http://localhost:8012",
                "analytics": "http://localhost:8013",
                "recommendation": "http://localhost:8014",
            }



_settings: GatewayServiceSettings | None = None


def get_settings() -> GatewayServiceSettings:
    global _settings
    if _settings is None:
        _settings = GatewayServiceSettings()
    return _settings
