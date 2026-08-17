"""Payment domain enums."""

from __future__ import annotations

from enum import Enum


class PaymentStatus(str, Enum):
    CREATED = "created"
    REQUIRES_ACTION = "requires_action"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethodType(str, Enum):
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


class PaymentAttemptStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
