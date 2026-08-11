from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class WhiteLabelServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-whitelabel"
    port: int = 8018
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_whitelabel"


@lru_cache(maxsize=1)
def get_settings() -> WhiteLabelServiceSettings:
    return WhiteLabelServiceSettings()
