"""
Privacy engineering utilities.
Provides:
- PII detection and redaction
- K-anonymity enforcement
- Differential privacy noise addition
- Data minimization helpers
"""

from __future__ import annotations

import hashlib
import re
import secrets
from collections import Counter
from datetime import datetime, timezone
from typing import Any

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone_in": re.compile(r"(?:\+91|0)?[6-9]\d{9}\b"),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ip_v4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "date_iso": re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
}



def detect_pii(text: str) -> dict[str, list[str]]:
    """Detect PII patterns in a text string."""
    found = {}
    for pii_type, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[pii_type] = matches
    return found


def redact_pii(text: str, replacement: str = "[REDACTED]") -> str:
    """Redact PII from text."""
    redacted = text
    for pattern in PII_PATTERNS.values():
        redacted = pattern.sub(replacement, redacted)
    return redacted


def k_anonymize(values: list[Any], k: int = 5) -> list[Any]:
    """Enforce k-anonymity."""
    counter = Counter(values)
    generalized = {}
    for value, count in counter.items():
        if count < k:
            h = hashlib.sha256(str(value).encode()).hexdigest()[:8]
            generalized[value] = f"bucket_{h}"
    return [generalized.get(v, v) for v in values]


def add_differential_privacy_noise(
    value: float, epsilon: float = 1.0, sensitivity: float = 1.0
) -> float:
    """Add Laplace noise for differential privacy."""
    import random
    import math

    scale = sensitivity / epsilon
    u = random.uniform(-0.5, 0.5)
    noise = -scale * (1 if u < 0 else -1) * math.log(1 - 2 * abs(u))
    return value + noise


def pseudonymize(value: str, salt: str = "faccp") -> str:
    """Create a stable pseudonym (HMAC-SHA256)."""
    import hmac

    return hmac.new(salt.encode(), value.encode(), hashlib.sha256).hexdigest()


def data_minimization_filter(
    data: dict[str, Any],
    allowed_fields: set[str],
    sensitive_fields: set[str] | None = None,
) -> dict[str, Any]:
    sensitive_fields = sensitive_fields or set()
    forbidden = sensitive_fields - allowed_fields
    return {k: v for k, v in data.items() if k in allowed_fields and k not in forbidden}


class ConsentAwareField:
    def __init__(self, field_name: str, requires_consent: str):
        self.field_name = field_name
        self.requires_consent = requires_consent

    def can_expose(self, consumer_consents: dict[str, bool]) -> bool:
        return consumer_consents.get(self.requires_consent, False)


def anonymize_for_analytics(record: dict[str, Any]) -> dict[str, Any]:
    out = {}
    sensitive_keys = {
        "name", "first_name", "last_name", "email", "phone", "address",
        "address_line1", "address_line2", "postal_code", "id_number",
        "pan", "aadhaar", "ssn", "dob", "date_of_birth", "ip_address",
        "user_agent", "device_fingerprint",
    }
    for k, v in record.items():
        if k.lower() in sensitive_keys:
            continue
        if k in ("consumer_id", "user_id", "retailer_id", "driver_id"):
            out[k] = pseudonymize(str(v), salt="faccp_analytics")
        elif isinstance(v, datetime):
            out[k] = v.date().isoformat()
        elif isinstance(v, (int, float)):
            if abs(v) > 1000:
                out[k] = round(v, -2)
            else:
                out[k] = v
        else:
            out[k] = v
    return out
