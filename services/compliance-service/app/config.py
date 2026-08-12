"""Compliance service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class ComplianceServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-compliance"
    port: int = 8007
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_compliance"

    cache_ttl_seconds: int = 300
    fail_closed: bool = True
    enforce_dry_days: bool = True
    enforce_hours: bool = True
    enforce_quantity_limits: bool = True
    enforce_licenses: bool = True


_settings: ComplianceServiceSettings | None = None


def get_settings() -> ComplianceServiceSettings:
    global _settings
    if _settings is None:
        _settings = ComplianceServiceSettings()
    return _settings
