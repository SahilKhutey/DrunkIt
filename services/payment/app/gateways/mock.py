import uuid
from services.payment.app.gateways.base import PaymentGateway


class MockGateway(PaymentGateway):

    async def create_payment(
        self,
        amount: int,
        currency: str,
        order_id: str,
        idempotency_key: str,
    ) -> dict:

        return {
            "provider_payment_id": f"mock_{uuid.uuid4()}",
            "status": "AUTHORIZED",
            "amount": amount,
            "currency": currency,
        }

    async def capture(
        self,
        provider_payment_id: str,
        amount: int,
    ) -> dict:

        return {
            "status": "CAPTURED",
            "provider_payment_id": provider_payment_id,
            "amount": amount,
        }

    async def refund(
        self,
        provider_payment_id: str,
        amount: int,
        idempotency_key: str,
    ) -> dict:

        return {
            "status": "REFUNDED",
            "provider_refund_id": f"ref_{uuid.uuid4()}",
            "provider_payment_id": provider_payment_id,
            "amount": amount,
        }

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> dict:

        return {
            "provider_payment_id": provider_payment_id,
            "status": "CAPTURED",
            "amount": 100000,
        }

    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:

        if signature == "invalid_sig":
            raise ValueError("INVALID_SIGNATURE")
        return True
