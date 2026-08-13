"""Data sanitization and normalization utilities."""

from __future__ import annotations

import re


def sanitize_email(email: str) -> str:
    """Strips whitespace and converts email to lowercase."""
    if not email:
        return ""
    return email.strip().lower()


def format_e164_phone(phone: str, default_country: str = "+91") -> str:
    """Normalizes phone number string to standard E.164 format."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    if len(digits) == 10:
        return f"{default_country}{digits}"
    return f"+{digits}" if digits else ""
