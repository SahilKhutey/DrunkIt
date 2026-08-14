"""Saga state enum definitions."""

from __future__ import annotations

from enum import Enum


class SagaState(str, Enum):
    CREATED = "created"
    COMPLIANCE_PENDING = "compliance_pending"
    RISK_PENDING = "risk_pending"
    PAYMENT_PENDING = "payment_pending"
    INVENTORY_PENDING = "inventory_pending"
    FULFILLMENT_PENDING = "fulfillment_pending"
    DELIVERY_PENDING = "delivery_pending"
    VERIFICATION_PENDING = "verification_pending"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"
