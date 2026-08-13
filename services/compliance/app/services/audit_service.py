from datetime import datetime, timezone
from uuid import uuid4

from services.compliance.app.models.audit_event import hash_payload


class AuditService:

    def __init__(self):
        self.audit_events: dict[str, list[dict]] = {}

    async def record(
        self,
        action: str,
        subject_id: str,
        metadata: dict | None = None,
        actor_type: str = "SYSTEM",
        actor_id: str | None = None,
        subject_type: str = "COMPLIANCE_SUBJECT",
    ) -> dict:

        payload = {
            "action": action,
            "subject_id": subject_id,
            "metadata": metadata or {},
        }
        p_hash = hash_payload(payload)

        event = {
            "id": str(uuid4()),
            "event_type": action,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "payload_hash": p_hash,
            "created_at": datetime.now(timezone.utc),
        }
        self.audit_events.setdefault(subject_id, []).append(event)
        return event

    async def get_audits(self, subject_id: str) -> list[dict]:
        return self.audit_events.get(subject_id, [])
