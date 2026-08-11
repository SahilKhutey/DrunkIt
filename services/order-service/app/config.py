from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class OrderServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-order"
    port: int = 8006
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_order"


@lru_cache(maxsize=1)
def get_settings() -> OrderServiceSettings:
    return OrderServiceSettings()
