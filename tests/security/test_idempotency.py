"""Unit tests for idempotency key replay protection and payload hash mismatch detection."""

import pytest
from fastapi import HTTPException
from faccp_platform.security.idempotency import (
    IdempotencyRecord,
    calculate_payload_hash,
    validate_idempotency_key,
)


def test_idempotency_key_replay_protection():
    """Verify identical payload returns cached response, while modified payload raises 409 Conflict."""
    payload_a = {"amount": 100, "currency": "USD"}
    hash_a = calculate_payload_hash(payload_a)

    rec = IdempotencyRecord(
        key="key_1",
        user_id="user_123",
        request_hash=hash_a,
        response_status=200,
        response_body={"status": "success"},
    )

    # Identical payload -> returns cached response
    res = validate_idempotency_key(rec, hash_a)
    assert res == {"status": "success"}

    # Different payload with same key -> raises 409 Conflict
    payload_b = {"amount": 500, "currency": "USD"}
    hash_b = calculate_payload_hash(payload_b)

    with pytest.raises(HTTPException) as exc_info:
        validate_idempotency_key(rec, hash_b)

    assert exc_info.value.status_code == 409
    assert "Idempotency key reused with different request payload" in exc_info.value.detail
