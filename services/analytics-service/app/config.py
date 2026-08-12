"""Analytics service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class AnalyticsServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-analytics"
    port: int = 8013
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_analytics"


_settings: AnalyticsServiceSettings | None = None


def get_settings() -> AnalyticsServiceSettings:
    global _settings
    if _settings is None:
        _settings = AnalyticsServiceSettings()
    return _settings
