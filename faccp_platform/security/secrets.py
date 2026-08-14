"""Secret resolution provider."""

from __future__ import annotations

import os


class SecretProvider:
    """Secret provider retrieving credentials from environment or secret vault."""

    def __init__(self, secrets_dict: dict[str, str] | None = None) -> None:
        self.secrets_dict = secrets_dict or {}

    def get(self, name: str, default: str | None = None) -> str:
        """Get secret by name."""
        if name in self.secrets_dict:
            return self.secrets_dict[name]
        val = os.getenv(name)
        if val is not None:
            return val
        if default is not None:
            return default
        raise RuntimeError(f"Secret not configured: {name}")
