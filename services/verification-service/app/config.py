from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class VerificationServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-verification"
    port: int = 8010
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_verification"


@lru_cache(maxsize=1)
def get_settings() -> VerificationServiceSettings:
    return VerificationServiceSettings()
