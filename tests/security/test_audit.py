"""Unit tests for tamper-evident audit hash chain verification."""

import pytest
from faccp_platform.audit.service import hash_record, verify_chain


def test_audit_hash_chain():
    """Verify SHA-256 canonical audit chain validation and tampering detection."""
    prev = "0" * 64
    r1 = {"action": "order.created", "actor": "user_123"}
    h1 = hash_record(prev, r1)

    r2 = {"action": "order.completed", "actor": "user_123"}
    h2 = hash_record(h1, r2)

    chain = [
        {"previous_hash": prev, "record_hash": h1, "data": r1},
        {"previous_hash": h1, "record_hash": h2, "data": r2},
    ]

    assert verify_chain(chain) is True

    # Tamper with record 1
    chain_tampered = [
        {"previous_hash": prev, "record_hash": h1, "data": {"action": "order.created", "actor": "attacker"}},
        {"previous_hash": h1, "record_hash": h2, "data": r2},
    ]

    assert verify_chain(chain_tampered) is False
