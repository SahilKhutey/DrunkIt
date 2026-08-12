from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class GatewaySettings(BaseServiceSettings):
    service_name: str = "faccp-gateway"
    port: int = 8000

    identity_service_url: str = "http://localhost:8001"
    consumer_service_url: str = "http://localhost:8002"
    retailer_service_url: str = "http://localhost:8003"
    catalog_service_url: str = "http://localhost:8004"
    inventory_service_url: str = "http://localhost:8005"
    order_service_url: str = "http://localhost:8006"
    compliance_service_url: str = "http://localhost:8007"
    audit_service_url: str = "http://localhost:8008"
    risk_service_url: str = "http://localhost:8009"
    verification_service_url: str = "http://localhost:8010"
    delivery_service_url: str = "http://localhost:8011"
    notification_service_url: str = "http://localhost:8012"
    payment_service_url: str = "http://localhost:8013"
    pricing_service_url: str = "http://localhost:8014"
    analytics_service_url: str = "http://localhost:8015"
    realtime_service_url: str = "http://localhost:8016"
    recommendation_service_url: str = "http://localhost:8017"
    whitelabel_service_url: str = "http://localhost:8018"
    reporting_service_url: str = "http://localhost:8019"
    support_service_url: str = "http://localhost:8020"




@lru_cache(maxsize=1)
def get_settings() -> GatewaySettings:
    return GatewaySettings()

