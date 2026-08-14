"""Canonical Kafka topic and event string definitions."""

from __future__ import annotations


class Topics:
    ORDER_EVENTS = "faccp.order.events"
    PAYMENT_EVENTS = "faccp.payment.events"
    INVENTORY_EVENTS = "faccp.inventory.events"
    IDENTITY_EVENTS = "faccp.identity.events"
    COMPLIANCE_EVENTS = "faccp.compliance.events"
    RISK_EVENTS = "faccp.risk.events"
    FULFILLMENT_EVENTS = "faccp.fulfillment.events"
    DELIVERY_EVENTS = "faccp.delivery.events"
    AUDIT_EVENTS = "faccp.audit.events"
    DEAD_LETTER = "faccp.events.dlq"

    # Standardized DrunkIt V1 Canonical Topics
    DRUNKIT_ORDER = "drunkit.order.v1"
    DRUNKIT_PAYMENT = "drunkit.payment.v1"
    DRUNKIT_INVENTORY = "drunkit.inventory.v1"
    DRUNKIT_COMPLIANCE = "drunkit.compliance.v1"
    DRUNKIT_DELIVERY = "drunkit.delivery.v1"
    DRUNKIT_SECURITY = "drunkit.security.v1"

    # Specific event topic routing keys
    ORDER_CREATED = "order.created"
    ORDER_CANCELLED = "order.cancelled"

    COMPLIANCE_CHECK_REQUESTED = "compliance.check_requested"
    COMPLIANCE_APPROVED = "compliance.approved"
    COMPLIANCE_REJECTED = "compliance.rejected"

    RISK_CHECK_REQUESTED = "risk.check_requested"
    RISK_APPROVED = "risk.approved"
    RISK_REJECTED = "risk.rejected"

    PAYMENT_AUTHORIZATION_REQUESTED = "payment.authorization_requested"
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUND_REQUESTED = "payment.refund_requested"
    PAYMENT_REFUNDED = "payment.refunded"

    INVENTORY_RESERVATION_REQUESTED = "inventory.reservation_requested"
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_FAILED = "inventory.failed"
    INVENTORY_RELEASED = "inventory.released"

    FULFILLMENT_REQUESTED = "fulfillment.requested"
    FULFILLMENT_CREATED = "fulfillment.created"
    FULFILLMENT_READY = "fulfillment.ready"
    FULFILLMENT_FAILED = "fulfillment.failed"

    DELIVERY_REQUESTED = "delivery.requested"
    DELIVERY_CREATED = "delivery.created"
    DELIVERY_ASSIGNED = "delivery.assigned"
    DELIVERY_PICKED_UP = "delivery.picked_up"
    DELIVERY_IN_TRANSIT = "delivery.in_transit"
    DELIVERY_ARRIVED = "delivery.arrived"

    VERIFICATION_STARTED = "verification.started"
    VERIFICATION_COMPLETED = "verification.completed"

    ORDER_COMPLETED = "order.completed"
    ORDER_COMPENSATION_REQUIRED = "order.compensation_required"

    @classmethod
    def all(cls) -> list[str]:
        return [
            value
            for name, value in vars(cls).items()
            if name.isupper() and isinstance(value, str)
        ]
