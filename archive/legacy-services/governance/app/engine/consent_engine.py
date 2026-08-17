from datetime import datetime, timezone
from uuid import uuid4


class ConsentEngine:

    def __init__(self):
        self.consents: dict[str, dict] = {}

    async def grant_consent(
        self,
        subject_id: str,
        consent_type: str,
        version: str = "1.0",
        source: str = "MOBILE_APP",
    ) -> dict:

        cid = str(uuid4())
        rec = {
            "id": cid,
            "subject_id": subject_id,
            "consent_type": consent_type,
            "version": version,
            "status": "GRANTED",
            "granted_at": datetime.now(timezone.utc),
            "withdrawn_at": None,
            "source": source,
        }
        self.consents[f"{subject_id}:{consent_type}"] = rec
        return rec

    async def withdraw_consent(self, subject_id: str, consent_type: str) -> dict:
        key = f"{subject_id}:{consent_type}"
        rec = self.consents.get(key)
        if not rec:
            raise ValueError("CONSENT_RECORD_NOT_FOUND")

        rec["status"] = "WITHDRAWN"
        rec["withdrawn_at"] = datetime.now(timezone.utc)
        return rec

    async def has_valid_consent(self, subject_id: str, consent_type: str) -> bool:
        key = f"{subject_id}:{consent_type}"
        rec = self.consents.get(key)
        return rec is not None and rec["status"] == "GRANTED"
