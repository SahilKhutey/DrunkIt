class PaymentStatusResponse:

    def __init__(self, status: str):
        self.status = status


class PaymentClient:

    def __init__(self, http=None):
        self.http = http

    async def authorize(
        self,
        order_id: str,
        amount: int,
        currency: str,
        idempotency_key: str,
    ) -> dict:

        return {
            "payment_id": f"pay_{order_id}",
            "status": "AUTHORIZED",
            "amount": amount,
        }

    async def get_status(self, payment_id: str) -> PaymentStatusResponse:
        if payment_id == "pay_failed":
            return PaymentStatusResponse(status="FAILED")
        return PaymentStatusResponse(status="AUTHORIZED")
