"""JWT Verifier implementation."""

from __future__ import annotations

from typing import Any
import jwt
from .claims import TokenClaims


class JWTVerifier:
    """Strict JWT verifier validating signature, issuer, audience, expiration, and required claims."""

    def __init__(
        self,
        issuer: str,
        audience: str,
        public_key: str,
        algorithm: str = "RS256",
    ) -> None:
        self.issuer = issuer
        self.audience = audience
        self.public_key = public_key
        self.algorithm = algorithm

    def verify(self, token: str) -> TokenClaims:
        """Verify token signature and claims strictly."""
        header = jwt.get_unverified_header(token)
        if header.get("alg") != self.algorithm:
            raise ValueError(f"Algorithm confusion detected: expected {self.algorithm}, got {header.get('alg')}")

        payload = jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
            issuer=self.issuer,
            audience=self.audience,
            options={
                "require": ["sub", "iss", "aud", "exp", "iat", "jti"],
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
            },
        )
        return TokenClaims(**payload)
