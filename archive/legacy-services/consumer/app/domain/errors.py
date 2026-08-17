"""Consumer domain exception definitions."""

from __future__ import annotations


class ConsumerDomainError(Exception):
    """Base exception for consumer domain errors."""
    pass


class ConsumerNotFoundError(ConsumerDomainError):
    """Raised when a consumer cannot be found."""
    pass


class ConsumerAlreadyExistsError(ConsumerDomainError):
    """Raised when a consumer with the same identity already exists."""
    pass


class InvalidStateTransitionError(ConsumerDomainError):
    """Raised when an illegal consumer status transition is attempted."""
    pass
