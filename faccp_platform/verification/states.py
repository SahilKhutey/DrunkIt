"""Verification state enum definitions."""

from __future__ import annotations

from enum import Enum


class VerificationState(str, Enum):
    """Verification state machine states."""

    NOT_STARTED = "not_started"
    INITIATED = "initiated"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    MANUAL_REVIEW = "manual_review"
