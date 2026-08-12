"""Inventory service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class InventoryServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-inventory"
    port: int = 8005
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_inventory"

    reservation_ttl_minutes: int = 15


_settings: InventoryServiceSettings | None = None


def get_settings() -> InventoryServiceSettings:
    global _settings
    if _settings is None:
        _settings = InventoryServiceSettings()
    return _settings
