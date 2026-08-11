from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class ConsumerServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-consumer"
    port: int = 8002
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_consumer"


@lru_cache(maxsize=1)
def get_settings() -> ConsumerServiceSettings:
    return ConsumerServiceSettings()
