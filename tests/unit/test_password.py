"""Unit tests for password hashing and verification."""

from faccp_platform.security.password import hash_password, verify_password


def test_password_hashing():
    password = "StrongPassword!123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)
