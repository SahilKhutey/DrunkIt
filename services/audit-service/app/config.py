from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class AuditServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-audit"
    port: int = 8008
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_audit"


@lru_cache(maxsize=1)
def get_settings() -> AuditServiceSettings:
    return AuditServiceSettings()
