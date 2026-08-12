"""Retailer service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class RetailerServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-retailer"
    port: int = 8003
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_retailer"

    license_renewal_notice_days: int = 30
    require_license_verification: bool = True


_settings: RetailerServiceSettings | None = None


def get_settings() -> RetailerServiceSettings:
    global _settings
    if _settings is None:
        _settings = RetailerServiceSettings()
    return _settings
