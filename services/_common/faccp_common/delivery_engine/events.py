"""
Delivery Event Topics & Publisher.
"""

from __future__ import annotations

from typing import Any, ClassVar


class DeliveryEventTopics:
    TOPICS: ClassVar[list[str]] = [
        "delivery.requested",
        "delivery.planned",
        "delivery.assigned",
        "delivery.pickup.ready",
        "delivery.picked_up",
        "delivery.location.updated",
        "delivery.eta.updated",
        "delivery.arriving",
        "delivery.verification.required",
        "delivery.completed",
        "delivery.failed",
        "delivery.cancelled",
        "delivery.return.required",
        "delivery.incident.opened",
    ]


class DeliveryEventPublisher:
    """Publishes delivery lifecycle events to Kafka topics."""

    def build_event(self, event_type: str, delivery_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if event_type not in DeliveryEventTopics.TOPICS:
            raise ValueError(f"Invalid delivery event topic: {event_type}")
        return {
            "event_type": event_type,
            "delivery_id": delivery_id,
            "payload": payload,
        }
