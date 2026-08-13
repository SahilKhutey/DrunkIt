"""Support agent service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class SupportAgentServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-support-agent"
    port: int = 8016
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_support"


_settings: SupportAgentServiceSettings | None = None


def get_settings() -> SupportAgentServiceSettings:
    global _settings
    if _settings is None:
        _settings = SupportAgentServiceSettings()
    return _settings
