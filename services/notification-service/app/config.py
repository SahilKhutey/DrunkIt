from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class NotificationServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-notification"
    port: int = 8012


@lru_cache(maxsize=1)
def get_settings() -> NotificationServiceSettings:
    return NotificationServiceSettings()
