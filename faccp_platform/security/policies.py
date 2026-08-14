"""Password policy validation rules."""

from __future__ import annotations

import re


class PasswordPolicyError(ValueError):
    """Raised when password validation fails policy criteria."""
    pass


def validate_password(password: str, *, minimum_length: int = 12) -> None:
    """Enforce password strength policy rules."""
    if len(password) < minimum_length:
        raise PasswordPolicyError("Password is too short")

    if not re.search(r"[A-Z]", password):
        raise PasswordPolicyError("Password requires uppercase character")

    if not re.search(r"[a-z]", password):
        raise PasswordPolicyError("Password requires lowercase character")

    if not re.search(r"[0-9]", password):
        raise PasswordPolicyError("Password requires numeric character")

    if not re.search(r"[^A-Za-z0-9]", password):
        raise PasswordPolicyError("Password requires special character")
