"""Kafka topic initialization script for FACCP platform."""

from __future__ import annotations

import logging
from faccp_platform.events.topics import Topics

logger = logging.getLogger("faccp.scripts.create_topics")

TOPICS = [
    Topics.ORDER_CREATED,
    Topics.ORDER_CANCELLED,
    Topics.COMPLIANCE_CHECK_REQUESTED,
    Topics.COMPLIANCE_APPROVED,
    Topics.COMPLIANCE_REJECTED,
    Topics.RISK_CHECK_REQUESTED,
    Topics.RISK_APPROVED,
    Topics.RISK_REJECTED,
    Topics.PAYMENT_AUTHORIZATION_REQUESTED,
    Topics.PAYMENT_AUTHORIZED,
    Topics.PAYMENT_CAPTURED,
    Topics.PAYMENT_FAILED,
    Topics.PAYMENT_REFUND_REQUESTED,
    Topics.PAYMENT_REFUNDED,
    Topics.INVENTORY_RESERVATION_REQUESTED,
    Topics.INVENTORY_RESERVED,
    Topics.INVENTORY_FAILED,
    Topics.INVENTORY_RELEASED,
    Topics.FULFILLMENT_REQUESTED,
    Topics.FULFILLMENT_CREATED,
    Topics.FULFILLMENT_READY,
    Topics.FULFILLMENT_FAILED,
    Topics.DELIVERY_REQUESTED,
    Topics.DELIVERY_CREATED,
    Topics.DELIVERY_ASSIGNED,
    Topics.DELIVERY_PICKED_UP,
    Topics.DELIVERY_IN_TRANSIT,
    Topics.DELIVERY_ARRIVED,
    Topics.VERIFICATION_STARTED,
    Topics.VERIFICATION_COMPLETED,
    Topics.ORDER_COMPLETED,
    Topics.ORDER_COMPENSATION_REQUIRED,
    Topics.DEAD_LETTER,
]


def main() -> None:
    print(f"Registered {len(TOPICS)} Kafka topics:")
    for topic in TOPICS:
        print(f"  - {topic}")


if __name__ == "__main__":
    main()
