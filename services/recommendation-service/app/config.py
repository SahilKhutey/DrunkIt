from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class RecommendationServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-recommendation"
    port: int = 8017
    redis_url: str = "redis://localhost:6379/16"


@lru_cache(maxsize=1)
def get_settings() -> RecommendationServiceSettings:
    return RecommendationServiceSettings()
