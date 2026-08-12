"""Consumer service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class ConsumerServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-consumer"
    port: int = 8002
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_consumer"

    max_addresses_per_consumer: int = 10
    default_consumer_level: str = "C1_REGISTERED"
    require_kyc_for_level: str = "C3_FULL_KYC"


_settings: ConsumerServiceSettings | None = None


def get_settings() -> ConsumerServiceSettings:
    global _settings
    if _settings is None:
        _settings = ConsumerServiceSettings()
    return _settings
