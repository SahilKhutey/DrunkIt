"""Payment service: Payment Intents, Capture, Refunds & Double-Entry Ledger."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.db.models import DoubleEntryLedger, PaymentIntent, PaymentTransaction
from app.schemas.payment import (
    PaymentCaptureRequest, PaymentIntentCreate, PaymentRefundRequest,
)

logger = get_logger(__name__)


class PaymentService:
    """Financial transaction engine & double-entry ledger coordinator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # PAYMENT INTENTS
    # ============================================================
    async def create_intent(self, payload: PaymentIntentCreate) -> PaymentIntent:
        intent = PaymentIntent(
            order_id=payload.order_id,
            consumer_id=payload.consumer_id,
            amount_inr=payload.amount_inr,
            currency="INR",
            status="CREATED",
            gateway_provider=payload.gateway_provider,
        )
        self.db.add(intent)
        await self.db.commit()
        await self.db.refresh(intent)

        await self._publish("payment.intent_created", {
            "intent_id": intent.id, "order_id": intent.order_id, "amount": intent.amount_inr,
        })
        return intent

    async def get_intent(self, intent_id: str) -> PaymentIntent:
        result = await self.db.execute(select(PaymentIntent).where(PaymentIntent.id == intent_id))
        intent = result.scalar_one_or_none()
        if not intent:
            raise NotFoundError(f"Payment intent {intent_id} not found")
        return intent

    async def capture_payment(self, intent_id: str, payload: PaymentCaptureRequest) -> PaymentIntent:
        intent = await self.get_intent(intent_id)
        if intent.status == "CAPTURED":
            raise ConflictError(f"Payment intent {intent_id} already captured")

        intent.status = "CAPTURED"
        intent.gateway_transaction_id = payload.gateway_transaction_id

        tx = PaymentTransaction(
            intent_id=intent.id,
            transaction_type="CAPTURE",
            amount_inr=intent.amount_inr,
            status="SUCCESS",
        )
        self.db.add(tx)

        # Record Double-Entry Financial Ledger: Debit Escrow / Credit Merchant Account
        ledger_entry = DoubleEntryLedger(
            entry_id=f"ENT_{secrets.token_hex(8).upper()}",
            account_debit="CONSUMER_ESCROW",
            account_credit="RETAILER_PAYABLE",
            amount_inr=intent.amount_inr,
            reference_id=intent.order_id,
        )
        self.db.add(ledger_entry)

        await self.db.commit()
        await self.db.refresh(intent)

        await self._publish("payment.captured", {
            "intent_id": intent.id, "order_id": intent.order_id, "txn_id": payload.gateway_transaction_id,
        })
        return intent

    async def refund_payment(self, intent_id: str, payload: PaymentRefundRequest) -> PaymentIntent:
        intent = await self.get_intent(intent_id)
        if intent.status != "CAPTURED":
            raise BadRequestError(f"Cannot refund intent in status {intent.status}")

        intent.status = "REFUNDED"

        tx = PaymentTransaction(
            intent_id=intent.id,
            transaction_type="REFUND",
            amount_inr=intent.amount_inr,
            status="SUCCESS",
        )
        self.db.add(tx)

        # Reverse Ledger: Debit Merchant Account / Credit Consumer Refund
        ledger_entry = DoubleEntryLedger(
            entry_id=f"ENT_{secrets.token_hex(8).upper()}",
            account_debit="RETAILER_PAYABLE",
            account_credit="CONSUMER_REFUND",
            amount_inr=intent.amount_inr,
            reference_id=intent.order_id,
        )
        self.db.add(ledger_entry)

        await self.db.commit()
        await self.db.refresh(intent)

        await self._publish("payment.refunded", {
            "intent_id": intent.id, "order_id": intent.order_id, "reason": payload.reason,
        })
        return intent

    async def list_ledger_entries(self) -> list[DoubleEntryLedger]:
        result = await self.db.execute(
            select(DoubleEntryLedger).order_by(DoubleEntryLedger.created_at.desc())
        )
        return list(result.scalars().all())

    # ============================================================
    # HELPERS
    # ============================================================
    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-payment")
            await self.producer.publish("payment.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
