"""Fulfillment and Delivery domain enums."""

from __future__ import annotations

from enum import Enum


class FulfillmentStatus(str, Enum):
    CREATED = "created"
    RESERVING = "reserving"
    RESERVED = "reserved"
    PICKING = "picking"
    PACKING = "packing"
    READY_FOR_PICKUP = "ready_for_pickup"
    HANDED_TO_CARRIER = "handed_to_carrier"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliveryStatus(str, Enum):
    CREATED = "created"
    ASSIGNING = "assigning"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    VERIFICATION_PENDING = "verification_pending"
    DELIVERED = "delivered"
    RETURNING = "returning"
    RETURNED = "returned"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    EXPIRED = "expired"
