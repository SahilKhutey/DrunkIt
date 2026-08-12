"""
Token Standards as codified in Article 1 of the System Constitution (§1.3).
"""

from __future__ import annotations


class TokenStandards:
    ACCESS_TOKEN_LIFETIME_MINUTES = 15
    REFRESH_TOKEN_LIFETIME_DAYS = 7
    SESSION_ABSOLUTE_TIMEOUT_HOURS = 8
    JWT_ALGORITHM = "HS256"  # RS256 recommended for cross-service production
    JWT_ISSUER = "faccp-platform"
    JWT_AUDIENCE = "faccp-api"
    REQUIRE_TYPED_CLAIMS = True  # "type": "access" | "refresh"
    REQUIRE_JTI = True  # Unique token ID for revocation
    REQUIRE_ISSUED_AT = True
    REQUIRE_NOT_BEFORE = True
    REQUIRE_EXPIRATION = True
    ROTATE_REFRESH_TOKENS = True
    REVOKE_ON_PASSWORD_CHANGE = True
