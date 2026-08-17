"""Payment domain service executing intent creation, risk checks, and outbox emission."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import PaymentAttemptStatus, PaymentMethodType, PaymentStatus
from ..domain.events import PaymentCapturedEvent, PaymentCreatedEvent
from ..domain.state_machine import can_transition, transition
from ..models.payment import Payment
from ..models.payment_attempt import PaymentAttempt
from ..repositories.payment import PaymentRepository
from ..schemas.payment import CreatePaymentRequest
from .mock_provider import MockPaymentProvider
from .provider import PaymentCreateResult, PaymentProvider
from .risk_client import RiskClient


class PaymentService:
    """Business service handling payment intent creation, risk checks, and provider interaction."""

    def __init__(
        self,
        session: AsyncSession | None = None,
        provider: PaymentProvider | None = None,
        risk_client: RiskClient | None = None,
    ) -> None:
        self.session = session
        self.repository = PaymentRepository(session) if session is not None else None
        self.provider = provider or MockPaymentProvider()
        self.risk = risk_client or RiskClient()
        self.payments_mock: dict[str, dict] = {}
        self.payments = self.payments_mock
        self.idempotency_map: dict[str, dict] = {}


    async def create_payment(
        self, request: CreatePaymentRequest | Any
    ) -> tuple[Payment, PaymentCreateResult] | dict[str, Any]:
        """Execute risk-gated, idempotent payment intent creation."""
        if self.session is None:
            idemp_key = getattr(request, "idempotency_key", str(uuid.uuid4()))
            if idemp_key in self.idempotency_map:
                return self.idempotency_map[idemp_key]
            pid = str(uuid.uuid4())
            pay_dict = {
                "id": pid,
                "order_id": str(getattr(request, "order_id", "")),
                "customer_id": str(getattr(request, "consumer_id", getattr(request, "customer_id", ""))),
                "amount": getattr(request, "amount", 0),
                "currency": getattr(request, "currency", "INR"),
                "status": "AUTHORIZED",
                "provider_payment_id": f"mock_{pid[:8]}",
                "idempotency_key": idemp_key,
            }

            self.payments_mock[pid] = pay_dict
            self.idempotency_map[idemp_key] = pay_dict
            return pay_dict

        # 1. Idempotency Check
        existing = await self.repository.get_by_idempotency(request.idempotency_key)
        if existing:
            mock_res = PaymentCreateResult(
                provider_payment_id=existing.provider_payment_id or "mock_existing",
                status=existing.status,
            )
            return existing, mock_res

        # 2. Risk Evaluation Gate Check
        risk_payload = {
            "order_id": str(request.order_id),
            "consumer_id": str(request.consumer_id),
            "amount": float(request.amount),
            "currency": request.currency,
        }
        try:
            risk_res = await self.risk.evaluate(risk_payload)
            if risk_res.get("decision") == "block":
                raise ValueError(
                    f"Payment blocked by risk engine: {risk_res.get('reasons')}"
                )
        except Exception as exc:
            if "blocked by risk engine" in str(exc):
                raise

        # 3. Create Intent with Provider
        provider_res = await self.provider.create_payment(
            amount=Decimal(str(request.amount)),
            currency=request.currency,
            order_id=str(request.order_id),
            idempotency_key=request.idempotency_key,
        )

        payment_id = str(uuid.uuid4())
        initial_status = (
            PaymentStatus.REQUIRES_ACTION
            if provider_res.status == "requires_action"
            else PaymentStatus.PROCESSING
        )

        payment = Payment(
            id=payment_id,
            order_id=str(request.order_id),
            consumer_id=str(request.consumer_id),
            idempotency_key=request.idempotency_key,
            amount=Decimal(str(request.amount)),
            currency=request.currency,
            status=initial_status,
            method=getattr(request, "method", PaymentMethodType.UPI),
            provider="mock",
            provider_payment_id=provider_res.provider_payment_id,
        )
        self.session.add(payment)

        # 4. Record Payment Attempt
        attempt = PaymentAttempt(
            payment_id=payment_id,
            amount=Decimal(str(request.amount)),
            status=PaymentAttemptStatus.PROCESSING,
            provider_attempt_id=provider_res.provider_payment_id,
        )
        self.session.add(attempt)
        await self.session.flush()

        # 5. Transactional Outbox Event
        outbox = OutboxService(self.session)
        event = PaymentCreatedEvent(
            payment_id=payment.id,
            order_id=payment.order_id,
            consumer_id=payment.consumer_id,
            amount=str(payment.amount),
            currency=payment.currency,
            status=payment.status,
        )
        envelope = EventEnvelope(
            event_type=event.event_type,
            metadata=EventMetadata(producer="payment-service"),
            payload=event.payload(),
        )
        await outbox.enqueue(topic=Topics.PAYMENT_EVENTS, event=envelope)

        return payment, provider_res

    async def capture_payment(
        self, payment_id: str | uuid.UUID, amount: Decimal | None = None
    ) -> Payment | dict[str, Any]:
        """Capture authorized payment."""
        if self.session is None:
            pid = str(payment_id)
            if pid in self.payments_mock:
                self.payments_mock[pid]["status"] = "CAPTURED"
                return self.payments_mock[pid]
            return {"id": pid, "status": "CAPTURED"}

        payment = await self.repository.get(payment_id)
        if not payment:
            raise ValueError("Payment not found")

        # Validate State Transition
        transition(payment, PaymentStatus.CAPTURED)

        capture_res = await self.provider.capture_payment(
            provider_payment_id=payment.provider_payment_id or "",
            amount=amount or payment.amount,
        )

        payment.status = PaymentStatus.CAPTURED
        await self.session.flush()

        # Transactional Outbox Event
        outbox = OutboxService(self.session)
        event = PaymentCapturedEvent(
            payment_id=payment.id,
            order_id=payment.order_id,
            amount=str(payment.amount),
            currency=payment.currency,
        )
        envelope = EventEnvelope(
            event_type=event.event_type,
            metadata=EventMetadata(producer="payment-service"),
            payload=event.payload(),
        )
        await outbox.enqueue(topic=Topics.PAYMENT_EVENTS, event=envelope)

        return payment
