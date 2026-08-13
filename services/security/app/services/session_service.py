from datetime import datetime, timedelta, timezone
from uuid import uuid4


class SessionService:

    def __init__(self):
        self.sessions: dict[str, dict] = {}

    async def create_session(self, user_id: str, device_id: str | None = None) -> dict:
        sess_id = str(uuid4())
        now = datetime.now(timezone.utc)
        sess = {
            "id": sess_id,
            "user_id": user_id,
            "device_id": device_id,
            "status": "ACTIVE",
            "risk_score": 0.0,
            "created_at": now,
            "expires_at": now + timedelta(hours=24),
        }
        self.sessions[sess_id] = sess
        return sess

    async def revoke_session(self, session_id: str) -> dict:
        sess = self.sessions.get(session_id)
        if not sess:
            # Fallback: check if session_id is user_id
            for s in self.sessions.values():
                if s["user_id"] == session_id and s["status"] == "ACTIVE":
                    s["status"] = "REVOKED"
                    return s
            raise ValueError("SESSION_NOT_FOUND")

        sess["status"] = "REVOKED"
        return sess
