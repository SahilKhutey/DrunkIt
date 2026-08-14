"""Unit tests for JWT verification, claims, and algorithm security."""

import time
import jwt
import pytest
from faccp_platform.security.claims import TokenClaims
from faccp_platform.security.jwt import JWTVerifier

SECRET = "test-secret-key-32-chars-length!"


def test_jwt_claims_model():
    """Verify TokenClaims Pydantic model serialization."""
    claims = TokenClaims(
        sub="user_123",
        iss="faccp-auth",
        aud="faccp-api",
        exp=1000,
        iat=900,
        jti="jti_456",
        roles=["consumer"],
        permissions=["order:read"],
    )
    assert claims.sub == "user_123"
    assert "order:read" in claims.permissions


def test_jwt_verifier_success():
    """Verify successful verification of valid token signature and claims."""
    payload = {
        "sub": "user_123",
        "iss": "faccp-auth",
        "aud": "faccp-api",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "jti": "jti_789",
        "roles": ["consumer"],
        "permissions": ["order:read"],
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    verifier = JWTVerifier(issuer="faccp-auth", audience="faccp-api", public_key=SECRET, algorithm="HS256")
    claims = verifier.verify(token)
    assert claims.sub == "user_123"


def test_expired_token_rejected():
    """Verify expired token is rejected with ExpiredSignatureError."""
    payload = {
        "sub": "user_123",
        "iss": "faccp-auth",
        "aud": "faccp-api",
        "exp": int(time.time()) - 3600,
        "iat": int(time.time()) - 7200,
        "jti": "jti_789",
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    verifier = JWTVerifier(issuer="faccp-auth", audience="faccp-api", public_key=SECRET, algorithm="HS256")

    with pytest.raises(jwt.ExpiredSignatureError):
        verifier.verify(token)


def test_algorithm_confusion_rejected():
    """Verify token signed with wrong algorithm is rejected for algorithm confusion protection."""
    payload = {
        "sub": "user_123",
        "iss": "faccp-auth",
        "aud": "faccp-api",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "jti": "jti_789",
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    verifier = JWTVerifier(issuer="faccp-auth", audience="faccp-api", public_key=SECRET, algorithm="RS256")

    with pytest.raises(ValueError, match="Algorithm confusion detected"):
        verifier.verify(token)
