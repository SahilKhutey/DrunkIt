"""
Unit tests for core utilities module.
"""

from __future__ import annotations

from decimal import Decimal
import pytest

from faccp_common.utils.crypto import hash_sha256, generate_secure_token, compute_hmac_signature
from faccp_common.utils.sanitizers import sanitize_email, format_e164_phone
from faccp_common.utils.currency import round_currency, calculate_tax_breakdown


def test_crypto_utils():
    hashed = hash_sha256("test_string")
    assert len(hashed) == 64

    token = generate_secure_token(16)
    assert len(token) > 0

    hmac_sig = compute_hmac_signature("secret", "payload")
    assert len(hmac_sig) == 64


def test_sanitizer_utils():
    assert sanitize_email("  User@Example.COM ") == "user@example.com"
    assert format_e164_phone("9876543210") == "+919876543210"
    assert format_e164_phone("919876543210") == "+919876543210"


def test_currency_utils():
    assert round_currency(100.456) == Decimal("100.46")

    breakdown = calculate_tax_breakdown(100.0, 18.0)
    assert breakdown["subtotal"] == Decimal("100.00")
    assert breakdown["tax_amount"] == Decimal("18.00")
    assert breakdown["total_amount"] == Decimal("118.00")
