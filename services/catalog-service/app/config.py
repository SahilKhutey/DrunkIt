"""Catalog service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class CatalogServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-catalog"
    port: int = 8004
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_catalog"


_settings: CatalogServiceSettings | None = None


def get_settings() -> CatalogServiceSettings:
    global _settings
    if _settings is None:
        _settings = CatalogServiceSettings()
    return _settings
