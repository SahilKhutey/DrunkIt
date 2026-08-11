"""Compliance service configuration."""

from __future__ import annotations

from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class ComplianceServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-compliance"
    port: int = 8007
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_compliance"
    policies_path: str = "./policies"
    policy_cache_ttl_seconds: int = 300
    policy_evaluation_timeout_ms: int = 500


@lru_cache(maxsize=1)
def get_settings() -> ComplianceServiceSettings:
    return ComplianceServiceSettings()
