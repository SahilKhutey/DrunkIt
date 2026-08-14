"""JWT Token Claims definition."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TokenClaims(BaseModel):
    """TokenClaims representing authenticated user JWT payload."""

    sub: str
    iss: str = "faccp-platform"
    aud: str = "faccp-api"
    exp: int = 9999999999
    iat: int = 0
    jti: str = "jti-default"
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    session_id: str | None = None

    @property
    def user_id(self) -> str:
        """Alias for sub."""
        return self.sub
