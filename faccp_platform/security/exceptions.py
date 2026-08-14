"""Security exception definitions."""

from __future__ import annotations


class SecurityError(Exception):
    """Base exception for all security errors."""
    pass


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(SecurityError):
    """Raised when authorization checks fail."""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT token is invalid or expired."""
    pass


class AccountLockedError(AuthenticationError):
    """Raised when an account is locked due to excessive failed attempts."""
    pass
