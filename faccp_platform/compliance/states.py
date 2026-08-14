"""Compliance state enum definitions."""

from __future__ import annotations

from enum import Enum


class ComplianceState(str, Enum):
    """Compliance state machine states."""

    NOT_STARTED = "not_started"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REQUIRES_REVIEW = "requires_review"
    BLOCKED = "blocked"
