"""
Refresh Token Rotation & Replay Attack Detection (§15.4).
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any


class RefreshTokenRotation:
    """Handles refresh token rotation and token family revocation upon replay attacks."""

    def __init__(self) -> None:
        self._used_tokens: set[str] = set()
        self._revoked_families: set[str] = set()

    def is_family_revoked(self, family_id: str) -> bool:
        return family_id in self._revoked_families

    def rotate_token(self, refresh_token_jti: str, family_id: str) -> str:
        """Rotates token. If token JTI was already used, revokes token family."""
        if family_id in self._revoked_families:
            raise RuntimeError("Token family has been revoked due to security violation")

        if refresh_token_jti in self._used_tokens:
            self._revoked_families.add(family_id)
            raise RuntimeError("Refresh token reuse detected! Revoking entire token family.")

        self._used_tokens.add(refresh_token_jti)
        return str(uuid.uuid4())
