from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class ReportingSettings(BaseServiceSettings):
    service_name: str = "faccp-compliance-reporting"
    port: int = 8019
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_reporting"
    audit_service_url: str = "http://localhost:8008"
    risk_service_url: str = "http://localhost:8009"
    analytics_service_url: str = "http://localhost:8015"


@lru_cache(maxsize=1)
def get_settings() -> ReportingSettings:
    return ReportingSettings()
