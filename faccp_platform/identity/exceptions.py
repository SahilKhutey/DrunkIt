"""Identity exception definitions."""

from __future__ import annotations


class IdentityError(Exception):
    """Base exception for all identity domain errors."""
    pass


class UserAlreadyExistsError(IdentityError):
    """Raised when registering an email that is already registered."""
    pass


class UserNotFoundError(IdentityError):
    """Raised when a user cannot be found."""
    pass
