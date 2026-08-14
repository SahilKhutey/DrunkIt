"""Webhook payload DTO schema."""

from __future__ import annotations

from pydantic import BaseModel


class PaymentWebhookPayload(BaseModel):
    """Payload format sent by payment provider webhooks."""

    event_id: str
    event_type: str
    payment_id: str
    provider_payment_id: str
    status: str
    amount: str
    currency: str = "INR"
    created_at: str | None = None
