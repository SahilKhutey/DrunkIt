"""Payment service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class PaymentServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-payment"
    port: int = 8008
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_payment"


_settings: PaymentServiceSettings | None = None


def get_settings() -> PaymentServiceSettings:
    global _settings
    if _settings is None:
        _settings = PaymentServiceSettings()
    return _settings
