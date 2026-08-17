import hashlib
from datetime import datetime, timezone
from uuid import uuid4


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EvidenceEngine:

    def __init__(self):
        self.evidence_records: dict[str, dict] = {}

    async def record_evidence(
        self,
        evidence_type: str,
        subject_type: str,
        subject_id: str,
        source: str,
        external_reference: str | None = None,
        raw_data: bytes | None = None,
    ) -> dict:

        ev_id = f"ev_{uuid4().hex[:12]}"
        e_hash = hash_bytes(raw_data) if raw_data else hashlib.sha256(f"{subject_id}:{external_reference}".encode()).hexdigest()

        rec = {
            "id": str(uuid4()),
            "evidence_id": ev_id,
            "evidence_type": evidence_type,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "source": source,
            "external_reference": external_reference,
            "hash": e_hash,
            "captured_at": datetime.now(timezone.utc),
        }
        self.evidence_records[ev_id] = rec
        return rec

    async def verify_evidence(self, evidence_id: str, raw_data: bytes) -> bool:
        rec = self.evidence_records.get(evidence_id)
        if not rec:
            return False
        return hash_bytes(raw_data) == rec["hash"]
