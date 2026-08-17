from datetime import datetime, timezone
from uuid import uuid4
from services.governance.app.security.hashing import calculate_event_hash

GENESIS_HASH = "GENESIS"


class AuditEngine:

    def __init__(self, repository=None):
        self.repository = repository
        self.events: list[dict] = []
        self.sequence_counter = 1000

    async def record(self, event_data: dict) -> dict:
        prev_hash = GENESIS_HASH
        if self.events:
            prev_hash = self.events[-1]["event_hash"]

        self.sequence_counter += 1
        seq_num = self.sequence_counter
        event_id = event_data.get("event_id") or f"evt_{uuid4().hex[:12]}"

        raw_payload = event_data.get("payload") or event_data.get("metadata") or {}
        event_record = {
            "event_id": event_id,
            "sequence_number": seq_num,
            "event_type": event_data.get("event_type", "audit.event"),
            "occurred_at": event_data.get("occurred_at") or datetime.now(timezone.utc),
            "actor_type": event_data.get("actor_type", "SYSTEM"),
            "actor_id": event_data.get("actor_id"),
            "subject_type": event_data.get("subject_type"),
            "subject_id": event_data.get("subject_id"),
            "service": event_data.get("service", "unknown-service"),
            "action": event_data.get("action", "EXECUTE"),
            "outcome": event_data.get("outcome", "SUCCESS"),
            "correlation_id": event_data.get("correlation_id") or f"corr_{uuid4().hex[:8]}",
            "payload": raw_payload,
            "previous_hash": prev_hash,
        }

        e_hash = calculate_event_hash(prev_hash, event_record)
        event_record["event_hash"] = e_hash

        self.events.append(event_record)
        return event_record

    async def verify_chain(self) -> bool:
        prev_hash = GENESIS_HASH
        for event in self.events:
            event_copy = {k: v for k, v in event.items() if k != "event_hash"}
            expected = calculate_event_hash(prev_hash, event_copy)
            if expected != event["event_hash"]:
                return False
            prev_hash = event["event_hash"]
        return True
