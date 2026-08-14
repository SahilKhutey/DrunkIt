"""Payment domain events."""

from __future__ import annotations

from typing import ClassVar
from faccp_platform.events.contracts import DomainEvent


class PaymentCreatedEvent(DomainEvent):
    event_type: ClassVar[str] = "payment.created"
    payment_id: str
    order_id: str
    consumer_id: str
    amount: str
    currency: str = "INR"
    status: str


class PaymentCapturedEvent(DomainEvent):
    event_type: ClassVar[str] = "payment.captured"
    payment_id: str
    order_id: str
    amount: str
    currency: str = "INR"


class PaymentFailedEvent(DomainEvent):
    event_type: ClassVar[str] = "payment.failed"
    payment_id: str
    order_id: str
    reason: str
