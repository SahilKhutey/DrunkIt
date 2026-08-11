from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class PaymentServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-payment"
    port: int = 8013
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_payment"
    razorpay_key_id: str = "rzp_test_placeholder"
    razorpay_key_secret: str = "razorpay_secret_placeholder"
    stripe_secret_key: str = "sk_test_placeholder"
    default_currency: str = "INR"
    webhook_secret: str = "webhook_secret_placeholder"
    refund_max_days: int = 90
    platform_commission_pct: float = 8.0
    delivery_commission_pct: float = 5.0


@lru_cache(maxsize=1)
def get_settings() -> PaymentServiceSettings:
    return PaymentServiceSettings()
