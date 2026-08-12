"""Audit service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class AuditServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-audit"
    port: int = 8010
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_audit"


_settings: AuditServiceSettings | None = None


def get_settings() -> AuditServiceSettings:
    global _settings
    if _settings is None:
        _settings = AuditServiceSettings()
    return _settings
