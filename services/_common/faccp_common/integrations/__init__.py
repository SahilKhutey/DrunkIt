"""External integration hub — pluggable adapters for third-party services."""
from faccp_common.integrations.base import (
    IntegrationAdapter, IntegrationRegistry,
    IntegrationConfig,
)
from faccp_common.integrations.kyc import KYCAdapter, StubKYCAdapter, OnfidoKYCAdapter
from faccp_common.integrations.payment import PaymentGatewayAdapter, StubPaymentAdapter, RazorpayPaymentAdapter
from faccp_common.integrations.sms import SMSAdapter, TwilioSMSAdapter, StubSMSAdapter
from faccp_common.integrations.email import EmailAdapter, SendGridEmailAdapter, StubEmailAdapter

__all__ = [
    "IntegrationAdapter", "IntegrationRegistry", "IntegrationConfig",
    "KYCAdapter", "StubKYCAdapter", "OnfidoKYCAdapter",
    "PaymentGatewayAdapter", "StubPaymentAdapter", "RazorpayPaymentAdapter",
    "SMSAdapter", "TwilioSMSAdapter", "StubSMSAdapter",
    "EmailAdapter", "SendGridEmailAdapter", "StubEmailAdapter",
]
