"""Platform runtime error definitions."""

from __future__ import annotations


class PlatformError(Exception):
    """Base exception for all platform runtime errors."""
    pass


class ServiceStartupError(PlatformError):
    """Raised when a service fails to initialize or complete startup hooks."""
    pass


class ConfigurationError(PlatformError):
    """Raised when configuration validation fails."""
    pass
