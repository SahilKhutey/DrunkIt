from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class SupportAgentSettings(BaseServiceSettings):
    service_name: str = "faccp-support-agent"
    port: int = 8020
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_support"
    consumer_service_url: str = "http://localhost:8002"
    openai_api_key: str = ""


@lru_cache(maxsize=1)
def get_settings() -> SupportAgentSettings:
    return SupportAgentSettings()
