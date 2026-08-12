"""Order service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class OrderServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-order"
    port: int = 8006
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_order"

    compliance_service_url: str = "http://localhost:8007"
    inventory_service_url: str = "http://localhost:8005"
    payment_timeout_seconds: int = 900


_settings: OrderServiceSettings | None = None


def get_settings() -> OrderServiceSettings:
    global _settings
    if _settings is None:
        _settings = OrderServiceSettings()
    return _settings
