from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class RiskServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-risk"
    port: int = 8009
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_risk"


@lru_cache(maxsize=1)
def get_settings() -> RiskServiceSettings:
    return RiskServiceSettings()
