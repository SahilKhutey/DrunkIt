"""Delivery service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class DeliveryServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-delivery"
    port: int = 8009
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_delivery"


_settings: DeliveryServiceSettings | None = None


def get_settings() -> DeliveryServiceSettings:
    global _settings
    if _settings is None:
        _settings = DeliveryServiceSettings()
    return _settings
