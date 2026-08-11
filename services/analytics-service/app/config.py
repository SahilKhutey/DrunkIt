from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class AnalyticsServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-analytics"
    port: int = 8015
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_analytics"


@lru_cache(maxsize=1)
def get_settings() -> AnalyticsServiceSettings:
    return AnalyticsServiceSettings()
