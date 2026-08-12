"""Risk service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class RiskServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-risk"
    port: int = 8011
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_risk"


_settings: RiskServiceSettings | None = None


def get_settings() -> RiskServiceSettings:
    global _settings
    if _settings is None:
        _settings = RiskServiceSettings()
    return _settings
