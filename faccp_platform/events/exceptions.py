"""Event system exception definitions."""

from __future__ import annotations


class EventError(Exception):
    """Base exception for all event system errors."""
    pass


class EventPublishError(EventError):
    """Raised when publishing an event to Kafka fails."""
    pass


class EventConsumeError(EventError):
    """Raised when consuming or processing an event fails."""
    pass


class EventIdempotencyError(EventError):
    """Raised when duplicate processing is detected or idempotency check fails."""
    pass
