"""Unit tests for JWT Token generation and verification."""

import uuid
from faccp_platform.security.tokens import TokenService


def test_access_token():
    service = TokenService()
    user_id = uuid.uuid4()

    token = service.create_access_token(
        user_id=user_id,
        roles=["admin"],
        permissions=["users:read"],
    )

    payload = service.decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert "admin" in payload["roles"]
    assert "users:read" in payload["permissions"]
