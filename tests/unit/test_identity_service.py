import pytest
from faccp_common.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    FieldEncryption,
)

def test_password_hashing():
    raw_pass = "SecurePass123!"
    hashed = hash_password(raw_pass)
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPass", hashed) is False

def test_jwt_token_claims():
    secret = "faccp-identity-vault-super-secret-key-32bytes"
    token = create_access_token(
        subject="C-1001",
        secret=secret,
        algorithm="HS256",
        issuer="faccp-platform",
        audience="faccp-api",
        claims={"roles": ["CONSUMER"], "age_eligible": True},
    )
    decoded = decode_token(
        token,
        secret=secret,
        algorithm="HS256",
        issuer="faccp-platform",
        audience="faccp-api",
        expected_type="access",
    )
    assert decoded["sub"] == "C-1001"
    assert decoded["roles"] == ["CONSUMER"]
    assert decoded["age_eligible"] is True

def test_field_encryption():
    enc = FieldEncryption("dGVzdC1mZXJuZXQtS2V5LTMyLWJ5dGVzLXNlY3VyZSE=")
    phone = "+919876543210"
    encrypted = enc.encrypt(phone)
    assert encrypted != phone
    decrypted = enc.decrypt(encrypted)
    assert decrypted == phone

