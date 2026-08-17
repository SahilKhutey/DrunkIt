from datetime import datetime, timedelta, timezone
from uuid import uuid4


class RiderService:

    def __init__(self):
        self.authorizations: dict[str, list[dict]] = {}

    async def authorize_rider(
        self,
        rider_id: str,
        jurisdiction_id: str,
        authorization_type: str = "REGULATED_LAST_MILE",
    ) -> dict:

        now = datetime.now(timezone.utc)
        record = {
            "id": str(uuid4()),
            "rider_id": rider_id,
            "jurisdiction_id": jurisdiction_id,
            "authorization_type": authorization_type,
            "status": "VERIFIED",
            "valid_until": now + timedelta(days=180),
        }
        self.authorizations.setdefault(rider_id, []).append(record)
        return record

    async def get_eligibility(self, rider_id: str, jurisdiction_id: str) -> str:
        records = self.authorizations.get(rider_id, [])
        now = datetime.now(timezone.utc)
        for r in records:
            if r["status"] == "VERIFIED" and r["jurisdiction_id"] == jurisdiction_id and r["valid_until"] > now:
                return "ALLOW"
        return "DENY"
