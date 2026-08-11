from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class DeliveryServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-delivery"
    port: int = 8011
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_delivery"


@lru_cache(maxsize=1)
def get_settings() -> DeliveryServiceSettings:
    return DeliveryServiceSettings()
