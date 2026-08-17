"""Payment repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.payment import Payment
from ..models.payment_attempt import PaymentAttempt
from ..models.webhook import ProcessedPaymentWebhook


class PaymentRepository:
    """Repository handling payment persistence, lookup, and webhook deduplication."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, payment_id: str | uuid.UUID) -> Payment | None:
        """Fetch payment by payment_id."""
        pid_str = str(payment_id)
        result = await self.session.execute(select(Payment).where(Payment.id == pid_str))
        return result.scalar_one_or_none()

    async def get_by_order(self, order_id: str | uuid.UUID) -> Payment | None:
        """Fetch payment by order_id."""
        oid_str = str(order_id)
        result = await self.session.execute(select(Payment).where(Payment.order_id == oid_str))
        return result.scalar_one_or_none()

    async def get_by_idempotency(self, idempotency_key: str) -> Payment | None:
        """Fetch payment by idempotency key."""
        result = await self.session.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def get_by_provider_payment_id(self, provider_payment_id: str) -> Payment | None:
        """Fetch payment by provider_payment_id."""
        result = await self.session.execute(
            select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        )
        return result.scalar_one_or_none()

    async def is_webhook_processed(self, event_id: str) -> bool:
        """Check if webhook event_id was already processed."""
        result = await self.session.execute(
            select(ProcessedPaymentWebhook).where(ProcessedPaymentWebhook.event_id == event_id)
        )
        return result.scalar_one_or_none() is not None

    async def record_webhook(self, provider: str, event_id: str, payment_id: str | None = None) -> ProcessedPaymentWebhook:
        """Record processed webhook event for deduplication."""
        rec = ProcessedPaymentWebhook(provider=provider, event_id=event_id, payment_id=payment_id)
        self.session.add(rec)
        await self.session.flush()
        return rec
