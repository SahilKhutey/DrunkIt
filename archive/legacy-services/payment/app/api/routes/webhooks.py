"""Payment provider webhook handler routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.config.settings import get_settings
from faccp_platform.database.session import get_db_session
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ...domain.enums import PaymentStatus
from ...domain.events import PaymentCapturedEvent, PaymentFailedEvent
from ...domain.state_machine import can_transition, transition
from ...repositories.payment import PaymentRepository
from ...schemas.webhook import PaymentWebhookPayload
from ...services.webhook_security import verify_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/payment",
    status_code=status.HTTP_200_OK,
)
async def process_payment_webhook(
    request: Request,
    payload: PaymentWebhookPayload,
    session: AsyncSession = Depends(get_db_session),
    x_signature: str | None = Header(None, alias="X-Signature"),
):
    """Process incoming payment gateway webhook with HMAC verification and deduplication."""
    settings = get_settings()
    webhook_secret = getattr(settings, "WEBHOOK_SECRET", "mock_webhook_secret_key_12345")

    raw_body = await request.body()
    if x_signature and not verify_signature(raw_body, x_signature, webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook HMAC signature",
        )

    repo = PaymentRepository(session)
    if await repo.is_webhook_processed(payload.event_id):
        return {"status": "duplicate", "message": "Event already processed"}

    payment = await repo.get(payload.payment_id)
    if not payment:
        payment = await repo.get_by_provider_payment_id(payload.provider_payment_id)

    if payment:
        target_status_str = payload.status.lower()
        if target_status_str in PaymentStatus._value2member_map_:
            target_status = PaymentStatus(target_status_str)
            if can_transition(payment.status, target_status):
                transition(payment, target_status)

        outbox = OutboxService(session)
        if payment.status == PaymentStatus.CAPTURED:
            captured_evt = PaymentCapturedEvent(
                payment_id=payment.id,
                order_id=payment.order_id,
                amount=str(payment.amount),
                currency=payment.currency,
            )
            env = EventEnvelope(
                event_type=captured_evt.event_type,
                metadata=EventMetadata(producer="payment-service-webhook"),
                payload=captured_evt.payload(),
            )
            await outbox.enqueue(topic=Topics.PAYMENT_EVENTS, event=env)
        elif payment.status == PaymentStatus.FAILED:
            failed_evt = PaymentFailedEvent(
                payment_id=payment.id,
                order_id=payment.order_id,
                reason=payload.status,
            )
            env = EventEnvelope(
                event_type=failed_evt.event_type,
                metadata=EventMetadata(producer="payment-service-webhook"),
                payload=failed_evt.payload(),
            )
            await outbox.enqueue(topic=Topics.PAYMENT_EVENTS, event=env)

    await repo.record_webhook(
        provider="mock",
        event_id=payload.event_id,
        payment_id=payment.id if payment else None,
    )
    await session.commit()

    return {"status": "success", "event_id": payload.event_id}
