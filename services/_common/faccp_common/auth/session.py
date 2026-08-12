"""
Session Management Policy (§15.6).
"""

from __future__ import annotations


class SessionPolicy:
    IDLE_TIMEOUT_MINUTES = 30
    ABSOLUTE_TIMEOUT_HOURS = 8
    REFRESH_TOKEN_LIFETIME_DAYS = 7
    MAX_CONCURRENT_SESSIONS_PER_USER = 5
    ROTATE_SESSION_ID_ON_PRIVILEGE_CHANGE = True
    INVALIDATE_ALL_SESSIONS_ON_PASSWORD_CHANGE = True
    INVALIDATE_ALL_SESSIONS_ON_MFA_DISABLE = True


class SessionManager:
    """Manages active user sessions."""

    def __init__(self, db=None, redis_client=None) -> None:
        self.db = db
        self.redis = redis_client

    async def revoke_all_user_sessions(self, user_id: str, reason: str) -> int:
        return 0
