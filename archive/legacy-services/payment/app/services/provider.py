"""Abstract Payment Provider interface."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentCreateResult:
    provider_payment_id: str
    status: str
    client_secret: str | None = None


@dataclass
class PaymentCaptureResult:
    provider_payment_id: str
    status: str
    amount: Decimal


class PaymentProvider:
    """Abstract interface for payment gateway providers."""

    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        order_id: str,
        idempotency_key: str,
    ) -> PaymentCreateResult:
        raise NotImplementedError

    async def capture_payment(
        self,
        provider_payment_id: str,
        amount: Decimal | None = None,
    ) -> PaymentCaptureResult:
        raise NotImplementedError

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentCreateResult:
        raise NotImplementedError
