"""Order domain exceptions."""

from __future__ import annotations


class OrderDomainError(Exception):
    """Base exception for order domain errors."""
    pass


class InvalidStateTransitionError(OrderDomainError):
    """Raised when an illegal order status transition is attempted."""
    pass


class ComplianceCheckFailedError(OrderDomainError):
    """Raised when compliance engine returns DENY or REVIEW for order."""
    pass


class DuplicateIdempotencyKeyError(OrderDomainError):
    """Raised when duplicate idempotency key is submitted."""
    pass


class OrderNotFoundError(OrderDomainError):
    """Raised when requested order is not found."""
    pass
