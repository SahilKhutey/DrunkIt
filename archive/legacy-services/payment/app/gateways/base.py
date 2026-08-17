from abc import ABC, abstractmethod


class PaymentGateway(ABC):

    @abstractmethod
    async def create_payment(
        self,
        amount: int,
        currency: str,
        order_id: str,
        idempotency_key: str,
    ) -> dict:
        pass

    @abstractmethod
    async def capture(
        self,
        provider_payment_id: str,
        amount: int,
    ) -> dict:
        pass

    @abstractmethod
    async def refund(
        self,
        provider_payment_id: str,
        amount: int,
        idempotency_key: str,
    ) -> dict:
        pass

    @abstractmethod
    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> dict:
        pass

    @abstractmethod
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        pass
