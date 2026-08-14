"""Domain event contracts for FACCP services."""

from __future__ import annotations

from typing import Any, ClassVar
from pydantic import BaseModel


class DomainEvent(BaseModel):
    """Base class for all domain events."""

    event_type: ClassVar[str] = "domain.event"
    version: str = "1.0"

    def payload(self) -> dict[str, Any]:
        return self.model_dump(exclude={"version"})


class OrderCreatedEvent(DomainEvent):
    event_type: ClassVar[str] = "order.created"
    order_id: str
    consumer_id: str
    total: str = "0"
    total_amount: int | str | None = None
    currency: str = "INR"
    compliance_decision_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.total_amount is not None and self.total == "0":
            object.__setattr__(self, "total", str(self.total_amount))


class PaymentAuthorizedEvent(DomainEvent):
    event_type: ClassVar[str] = "payment.authorized"
    payment_id: str
    order_id: str
    amount: str
    currency: str = "INR"


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


class RiskEvaluatedEvent(DomainEvent):
    event_type: ClassVar[str] = "risk.evaluated"
    decision_id: str
    order_id: str
    decision: str
    risk_level: str
    score: float


class InventoryReservedEvent(DomainEvent):
    event_type: ClassVar[str] = "inventory.reserved"
    reservation_id: str
    order_id: str


class InventoryReservationFailedEvent(DomainEvent):
    event_type: ClassVar[str] = "inventory.reservation_failed"
    order_id: str
    reason: str


class FulfillmentReadyEvent(DomainEvent):
    event_type: ClassVar[str] = "fulfillment.ready"
    fulfillment_id: str
    order_id: str
    warehouse_id: str


class DeliveryAssignedEvent(DomainEvent):
    event_type: ClassVar[str] = "delivery.assigned"
    delivery_id: str
    order_id: str
    courier_id: str


class DeliveryDeliveredEvent(DomainEvent):
    event_type: ClassVar[str] = "delivery.delivered"
    delivery_id: str
    order_id: str
    delivered_at: str


class VerificationCompletedEvent(DomainEvent):
    event_type: ClassVar[str] = "verification.completed"
    verification_id: str
    delivery_id: str
    status: str
    method: str


class LoginSucceededEvent(DomainEvent):
    event_type: ClassVar[str] = "auth.login.success"
    user_id: str


class LoginFailedEvent(DomainEvent):
    event_type: ClassVar[str] = "auth.login.failure"
    username: str


class AccessDeniedEvent(DomainEvent):
    event_type: ClassVar[str] = "auth.access.denied"
    user_id: str
    resource: str


class ConsumerCreatedEvent(DomainEvent):
    event_type: ClassVar[str] = "consumer.created"
    consumer_id: str
    phone_number: str


class ConsumerActivatedEvent(DomainEvent):
    event_type: ClassVar[str] = "consumer.activated"
    consumer_id: str


class ConsumerVerificationCompletedEvent(DomainEvent):
    event_type: ClassVar[str] = "consumer.verification.completed"
    consumer_id: str
    verification_id: str
    status: str


class EligibilityEvaluatedEvent(DomainEvent):
    event_type: ClassVar[str] = "compliance.eligibility.evaluated"
    decision_id: str
    consumer_id: str
    jurisdiction_id: str
    decision: str
