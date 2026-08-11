from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class PricingServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-pricing"
    port: int = 8014
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_pricing"
    platform_commission_pct: float = 8.0


@lru_cache(maxsize=1)
def get_settings() -> PricingServiceSettings:
    return PricingServiceSettings()
