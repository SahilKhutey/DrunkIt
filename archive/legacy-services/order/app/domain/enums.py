"""Order domain enums."""

from __future__ import annotations

from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_COMPLIANCE = "pending_compliance"
    COMPLIANCE_FAILED = "compliance_failed"
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_FAILED = "payment_failed"
    CONFIRMED = "confirmed"
    FULFILLING = "fulfilling"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class FulfillmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    RESERVED = "reserved"
    PROCESSING = "processing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"


class CartStatus(str, Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CHECKED_OUT = "checked_out"
