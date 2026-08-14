"""Payment reconciliation service."""

from __future__ import annotations

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.payment import Payment
from ..repositories.payment import PaymentRepository
from .provider import PaymentProvider


class ReconciliationService:
    """Service auditing and reconciling local payment state against provider status."""

    def __init__(self, session: AsyncSession, provider: PaymentProvider) -> None:
        self.session = session
        self.repository = PaymentRepository(session)
        self.provider = provider

    async def reconcile_payment(self, payment: Payment) -> dict[str, Any]:
        """Compare local payment state with provider remote state."""
        if not payment.provider_payment_id:
            return {"status": "skipped", "reason": "no_provider_id"}

        remote = await self.provider.get_payment(payment.provider_payment_id)
        if remote.status != payment.status:
            return {
                "status": "mismatch",
                "payment_id": payment.id,
                "local_status": payment.status,
                "remote_status": remote.status,
            }
        return {"status": "match", "payment_id": payment.id}
