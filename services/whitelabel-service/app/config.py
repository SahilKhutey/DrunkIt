"""Whitelabel service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class WhitelabelServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-whitelabel"
    port: int = 8015
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_whitelabel"


_settings: WhitelabelServiceSettings | None = None


def get_settings() -> WhitelabelServiceSettings:
    global _settings
    if _settings is None:
        _settings = WhitelabelServiceSettings()
    return _settings
