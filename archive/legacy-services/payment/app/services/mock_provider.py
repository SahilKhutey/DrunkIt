"""Local Mock Payment Provider implementation."""

from __future__ import annotations

import uuid
from decimal import Decimal
from .provider import PaymentCaptureResult, PaymentCreateResult, PaymentProvider


class MockPaymentProvider(PaymentProvider):
    """Mock payment provider for local dev and unit testing without real money."""

    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        order_id: str,
        idempotency_key: str,
    ) -> PaymentCreateResult:
        pid = f"mock_{uuid.uuid4().hex}"
        return PaymentCreateResult(
            provider_payment_id=pid,
            status="requires_action",
            client_secret=f"mock_secret_{uuid.uuid4().hex}",
        )

    async def capture_payment(
        self,
        provider_payment_id: str,
        amount: Decimal | None = None,
    ) -> PaymentCaptureResult:
        return PaymentCaptureResult(
            provider_payment_id=provider_payment_id,
            status="captured",
            amount=amount or Decimal("1000.00"),
        )

    async def get_payment(
        self,
        provider_payment_id: str,
    ) -> PaymentCreateResult:
        return PaymentCreateResult(
            provider_payment_id=provider_payment_id,
            status="captured",
        )
