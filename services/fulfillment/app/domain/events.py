"""Fulfillment and Delivery domain events."""

from __future__ import annotations

from typing import ClassVar
from faccp_platform.events.contracts import DomainEvent


class InventoryReservedEvent(DomainEvent):
    event_type: ClassVar[str] = "inventory.reserved"
    reservation_id: str
    order_id: str


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
