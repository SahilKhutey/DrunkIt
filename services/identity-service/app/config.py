"""Identity service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class IdentityServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-identity"
    port: int = 8001
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_identity"

    password_min_length: int = 12
    max_login_attempts: int = 5
    login_lockout_minutes: int = 15
    session_absolute_timeout_hours: int = 8
    session_idle_timeout_minutes: int = 30
    max_concurrent_sessions: int = 5
    mfa_required_for_roles: list[str] = [
        "SUPER_ADMIN", "REGULATORY_ADMIN", "STATE_ADMIN",
        "RETAILER_OWNER", "STORE_MANAGER", "DELIVERY_AGENT",
        "DATA_PROTECTION_OFFICER", "FINANCE_ADMIN",
    ]
    refresh_token_rotation: bool = True
    webhook_secret: str = "change-me-webhook-secret"


_settings: IdentityServiceSettings | None = None


def get_settings() -> IdentityServiceSettings:
    global _settings
    if _settings is None:
        _settings = IdentityServiceSettings()
    return _settings
