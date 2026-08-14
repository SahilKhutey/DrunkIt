"""Domain enums for Consumer service."""

from __future__ import annotations

from enum import Enum


class ConsumerStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class VerificationStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class VerificationMethod(str, Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    THIRD_PARTY = "third_party"
    MANUAL = "manual"


class ProfileVisibility(str, Enum):
    PRIVATE = "private"
    STANDARD = "standard"
