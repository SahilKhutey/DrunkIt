"""
Payment orchestration — handles intent creation, provider integration,
capture, refund, and settlement.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.events import make_event
from faccp_common.exceptions import (
    BadRequestError, ConflictError, NotFoundError, StateTransitionError,
    UnauthorizedError,
)
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import (
    PaymentIntent, PaymentMethod, PaymentStatus,
    PaymentTransaction, Refund, Settlement, WebhookEvent,
)
from app.services.ledger import LedgerService
from app.schemas.payment import (
    CreateIntentRequest, IntentResponse, RefundRequest, RefundResponse,
    TransactionResponse, WebhookPayload,
)

logger = get_logger(__name__)
settings = get_settings()


class PaymentService:

    def __init__(
        self, db: AsyncSession, producer: EventProducer | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.db = db
        self.producer = producer
        self.ledger = LedgerService(db)
        self._http = http_client or httpx.AsyncClient(timeout=15.0)

    async def create_intent(
        self, payload: CreateIntentRequest, actor_id: str
    ) -> IntentResponse:
        if payload.amount <= 0:
            raise BadRequestError("Amount must be positive")
        if payload.method == PaymentMethod.COD.value:
            raise BadRequestError("Cash on delivery is not allowed for regulated products")
        intent = PaymentIntent(
            id=str(uuid.uuid4()),
            intent_number=self._new_intent_number(),
            order_id=payload.order_id,
            consumer_id=payload.consumer_id,
            retailer_id=payload.retailer_id,
            store_id=payload.store_id,
            amount=payload.amount,
            currency=payload.currency,
            platform_fee=payload.platform_fee,
            delivery_fee=payload.delivery_fee,
            tax_amount=payload.tax_amount,
            method=payload.method,
            status=PaymentStatus.PENDING.value,
            description=payload.description,
            metadata_json=payload.metadata or {},
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        self.db.add(intent)
        await self.db.commit()
        await self.db.refresh(intent)

        try:
            provider_response = await self._call_provider_create(intent)
            intent.provider = provider_response.get("provider")
            intent.provider_intent_id = provider_response.get("id")
            intent.provider_client_secret = provider_response.get("client_secret")
            await self.db.commit()
        except Exception as e:
            logger.exception("provider_intent_creation_failed", intent_id=intent.id)
            intent.status = PaymentStatus.FAILED.value
            intent.failure_reason = str(e)
            await self.db.commit()
            raise

        await self._emit("payment.intent_created", {
            "intent_id": intent.id, "intent_number": intent.intent_number,
            "order_id": intent.order_id, "amount": str(intent.amount),
            "method": intent.method, "status": intent.status,
        }, actor_id)
        return self._intent_to_response(intent)

    async def authorize(
        self, intent_id: str, provider_payment_id: str, actor_id: str
    ) -> TransactionResponse:
        intent = await self._get_intent(intent_id)
        if intent.status != PaymentStatus.PENDING.value:
            raise StateTransitionError(f"Cannot authorize intent in state {intent.status}")

        intent.status = PaymentStatus.AUTHORIZED.value
        intent.authorized_at = datetime.now(timezone.utc)
        await self.db.commit()

        fee = self._calc_provider_fee(intent.amount, intent.method)
        net = intent.amount - fee
        txn = PaymentTransaction(
            id=str(uuid.uuid4()),
            transaction_number=self._new_txn_number(),
            intent_id=intent.id,
            order_id=intent.order_id,
            consumer_id=intent.consumer_id,
            retailer_id=intent.retailer_id,
            amount=intent.amount,
            currency=intent.currency,
            fee_amount=Decimal("0"),
            net_amount=net,
            method=intent.method,
            provider=intent.provider or "unknown",
            provider_transaction_id=provider_payment_id,
            provider_fee=fee,
            provider_tax=Decimal("0"),
            status=PaymentStatus.AUTHORIZED.value,
            captured_at=datetime.now(timezone.utc),
        )
        self.db.add(txn)
        await self.db.commit()
        await self.db.refresh(txn)

        await self._emit("payment.authorized", {
            "intent_id": intent.id, "transaction_id": txn.id,
            "amount": str(txn.amount), "method": txn.method,
        }, actor_id)
        return self._txn_to_response(txn)

    async def capture(
        self, intent_id: str, actor_id: str
    ) -> TransactionResponse:
        intent = await self._get_intent(intent_id)
        if intent.status != PaymentStatus.AUTHORIZED.value:
            raise StateTransitionError(f"Cannot capture intent in state {intent.status}")

        result = await self.db.execute(
            select(PaymentTransaction).where(PaymentTransaction.intent_id == intent.id)
        )
        txn = result.scalar_one_or_none()
        if txn is None:
            raise NotFoundError("Transaction not found for intent")

        intent.status = PaymentStatus.CAPTURED.value
        intent.captured_at = datetime.now(timezone.utc)
        txn.status = PaymentStatus.CAPTURED.value

        await self.ledger.post_double_entry(
            description=f"Payment captured: {intent.intent_number}",
            debit_account=LedgerService.PROCESSOR_CLEARING,
            credit_account=LedgerService.CONSUMER_PAYABLE,
            amount=intent.amount,
            currency=intent.currency,
            credit_holder_id=intent.consumer_id,
            transaction_id=txn.id,
            correlation_id=intent.id,
        )

        if intent.platform_fee > 0:
            await self.ledger.post_double_entry(
                description=f"Platform fee for {intent.intent_number}",
                debit_account=LedgerService.CONSUMER_PAYABLE,
                credit_account=LedgerService.PLATFORM_REVENUE,
                amount=intent.platform_fee,
                currency=intent.currency,
                debit_holder_id=intent.consumer_id,
                transaction_id=txn.id,
            )

        if intent.tax_amount > 0:
            await self.ledger.post_double_entry(
                description=f"Tax for {intent.intent_number}",
                debit_account=LedgerService.CONSUMER_PAYABLE,
                credit_account=LedgerService.TAX_PAYABLE,
                amount=intent.tax_amount,
                currency=intent.currency,
                debit_holder_id=intent.consumer_id,
                transaction_id=txn.id,
            )

        net_to_retailer = intent.amount - intent.platform_fee - intent.tax_amount
        if net_to_retailer > 0:
            await self.ledger.post_double_entry(
                description=f"Net to retailer for {intent.intent_number}",
                debit_account=LedgerService.CONSUMER_PAYABLE,
                credit_account=LedgerService.RETAILER_RECEIVABLE,
                amount=net_to_retailer,
                currency=intent.currency,
                debit_holder_id=intent.consumer_id,
                credit_holder_id=intent.retailer_id,
                transaction_id=txn.id,
            )

        await self.db.commit()
        await self._emit("payment.captured", {
            "intent_id": intent.id, "transaction_id": txn.id,
            "amount": str(txn.amount), "net_to_retailer": str(net_to_retailer),
        }, actor_id)
        return self._txn_to_response(txn)

    async def create_refund(
        self, payload: RefundRequest, actor_id: str, actor_role: str
    ) -> RefundResponse:
        txn = await self._get_transaction(payload.transaction_id)
        if txn.status not in (PaymentStatus.CAPTURED.value, PaymentStatus.PARTIALLY_REFUNDED.value):
            raise StateTransitionError("Can only refund captured transactions")

        requires_2nd = payload.amount >= Decimal("50000")
        refund = Refund(
            id=str(uuid.uuid4()),
            refund_number=self._new_refund_number(),
            transaction_id=txn.id,
            intent_id=txn.intent_id,
            order_id=txn.order_id,
            consumer_id=txn.consumer_id,
            retailer_id=txn.retailer_id,
            amount=payload.amount,
            reason=payload.reason,
            initiated_by=actor_id,
            initiated_by_role=actor_role,
            status="PENDING",
            requires_2nd_approver=requires_2nd,
        )
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)

        if not requires_2nd:
            await self._process_refund(refund, actor_id)

        await self._emit("payment.refund_created", {
            "refund_id": refund.id, "refund_number": refund.refund_number,
            "amount": str(refund.amount), "requires_2nd_approver": requires_2nd,
        }, actor_id)
        return self._refund_to_response(refund)

    async def approve_refund(self, refund_id: str, approver_id: str) -> RefundResponse:
        result = await self.db.execute(select(Refund).where(Refund.id == refund_id))
        refund = result.scalar_one_or_none()
        if refund is None: raise NotFoundError("Refund not found")
        if refund.initiated_by == approver_id:
            raise BadRequestError("Initiator cannot approve their own refund (separation of duties)")
        if not refund.requires_2nd_approver:
            raise ConflictError("This refund does not require a second approver")
        if refund.second_approver_id is not None:
            raise ConflictError("Already approved by second approver")

        refund.second_approver_id = approver_id
        refund.second_approved_at = datetime.now(timezone.utc)
        await self.db.commit()

        await self._process_refund(refund, approver_id)
        return self._refund_to_response(refund)

    async def _process_refund(self, refund: Refund, actor_id: str) -> None:
        await self.ledger.post_double_entry(
            description=f"Refund: {refund.refund_number}",
            debit_account=LedgerService.RETAILER_RECEIVABLE,
            credit_account=LedgerService.CONSUMER_PAYABLE,
            amount=refund.amount,
            credit_holder_id=refund.consumer_id,
            debit_holder_id=refund.retailer_id,
            refund_id=refund.id,
        )
        refund.status = "COMPLETED"
        refund.processed_at = datetime.now(timezone.utc)
        await self.db.commit()

        await self._emit("payment.refund_completed", {
            "refund_id": refund.id, "amount": str(refund.amount),
        }, actor_id)

    async def process_webhook(
        self, provider: str, payload: WebhookPayload, signature: str | None
    ) -> dict[str, Any]:
        existing = await self.db.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == payload.event_id)
        )
        if existing.scalar_one_or_none() is not None:
            return {"status": "duplicate", "event_id": payload.event_id}

        webhook = WebhookEvent(
            id=str(uuid.uuid4()),
            provider=provider, event_id=payload.event_id,
            event_type=payload.event_type, payload=payload.model_dump(),
            signature=signature, received_at=datetime.now(timezone.utc),
        )
        self.db.add(webhook)
        webhook.processed = True
        webhook.processed_at = datetime.now(timezone.utc)
        await self.db.commit()
        return {"status": "processed", "event_id": payload.event_id}

    async def generate_settlement(
        self, holder_type: str, holder_id: str, period_start: datetime, period_end: datetime
    ) -> Settlement:
        from sqlalchemy import func
        account = (
            LedgerService.RETAILER_RECEIVABLE if holder_type == "retailer"
            else LedgerService.DELIVERY_RECEIVABLE
        )
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(LedgerEntry.credit), 0).label("credit"),
                func.coalesce(func.sum(LedgerEntry.debit), 0).label("debit"),
                func.count(LedgerEntry.id).label("count"),
            ).where(
                LedgerEntry.account_type == account,
                LedgerEntry.account_holder_id == holder_id,
                LedgerEntry.posted_at >= period_start,
                LedgerEntry.posted_at <= period_end,
            )
        )
        row = result.one()
        gross = Decimal(str(row.credit)) - Decimal(str(row.debit))
        if gross <= 0:
            raise BadRequestError("No balance to settle")
        fees = gross * Decimal("0.02")
        tax = Decimal("0")
        net = gross - fees - tax

        settlement = Settlement(
            id=str(uuid.uuid4()),
            settlement_number=self._new_settlement_number(),
            settlement_type=holder_type,
            holder_id=holder_id,
            period_start=period_start,
            period_end=period_end,
            gross_amount=gross,
            fees=fees,
            tax_withheld=tax,
            net_amount=net,
            transaction_count=row.count,
            status="PENDING",
        )
        self.db.add(settlement)
        await self.db.commit()
        await self.db.refresh(settlement)

        await self._emit("payment.settlement_generated", {
            "settlement_id": settlement.id, "holder_type": holder_type,
            "holder_id": holder_id, "net_amount": str(net),
        }, "system")
        return settlement

    async def _call_provider_create(self, intent: PaymentIntent) -> dict[str, Any]:
        if intent.method == "UPI":
            return {
                "provider": "razorpay",
                "id": f"rzp_{uuid.uuid4().hex[:16]}",
                "client_secret": f"secret_{uuid.uuid4().hex}",
            }
        elif intent.method == "CARD":
            return {
                "provider": "stripe",
                "id": f"pi_{uuid.uuid4().hex[:24]}",
                "client_secret": f"pi_{uuid.uuid4().hex[:24]}_secret_{uuid.uuid4().hex[:16]}",
            }
        return {"provider": "mock", "id": f"mock_{uuid.uuid4().hex[:16]}", "client_secret": "secret"}

    def _calc_provider_fee(self, amount: Decimal, method: str) -> Decimal:
        if method == "UPI":
            return amount * Decimal("0.002")
        elif method == "CARD":
            return amount * Decimal("0.02")
        return Decimal("0")

    async def _get_intent(self, intent_id: str) -> PaymentIntent:
        result = await self.db.execute(select(PaymentIntent).where(PaymentIntent.id == intent_id))
        i = result.scalar_one_or_none()
        if i is None: raise NotFoundError("Intent not found")
        return i

    async def _get_transaction(self, transaction_id: str) -> PaymentTransaction:
        result = await self.db.execute(select(PaymentTransaction).where(PaymentTransaction.id == transaction_id))
        t = result.scalar_one_or_none()
        if t is None: raise NotFoundError("Transaction not found")
        return t

    def _new_intent_number(self) -> str:
        return f"PAY-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:10].upper()}"

    def _new_txn_number(self) -> str:
        return f"TXN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:10].upper()}"

    def _new_refund_number(self) -> str:
        return f"REF-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:10].upper()}"

    def _new_settlement_number(self) -> str:
        return f"STL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:10].upper()}"

    def _intent_to_response(self, i: PaymentIntent) -> IntentResponse:
        return IntentResponse(
            id=i.id, intent_number=i.intent_number, order_id=i.order_id,
            amount=i.amount, currency=i.currency, method=i.method,
            status=i.status, provider=i.provider,
            provider_intent_id=i.provider_intent_id,
            provider_client_secret=i.provider_client_secret,
            expires_at=i.expires_at, created_at=i.created_at,
        )

    def _txn_to_response(self, t: PaymentTransaction) -> TransactionResponse:
        return TransactionResponse(
            id=t.id, transaction_number=t.transaction_number, intent_id=t.intent_id,
            order_id=t.order_id, amount=t.amount, net_amount=t.net_amount,
            currency=t.currency, method=t.method, provider=t.provider,
            status=t.status, captured_at=t.captured_at,
        )

    def _refund_to_response(self, r: Refund) -> RefundResponse:
        return RefundResponse(
            id=r.id, refund_number=r.refund_number, transaction_id=r.transaction_id,
            amount=r.amount, reason=r.reason, status=r.status,
            requires_2nd_approver=r.requires_2nd_approver,
            second_approved_at=r.second_approved_at, processed_at=r.processed_at,
            created_at=r.created_at,
        )

    async def _emit(self, event_type: str, payload: dict[str, Any], actor_id: str | None) -> None:
        if self.producer is None: return
        try:
            event = make_event(event_type=event_type, payload=payload, producer=settings.service_name, user_id=actor_id)
            await self.producer.publish(topic="payment.events", payload=event)
        except Exception:
            logger.exception("event_emit_failed", event_type=event_type)
