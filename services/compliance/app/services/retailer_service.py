from datetime import datetime, timedelta, timezone
from uuid import uuid4


class RetailerService:

    def __init__(self):
        self.licenses: dict[str, list[dict]] = {}

    async def add_license(
        self,
        retailer_id: str,
        license_number: str,
        jurisdiction_id: str,
        license_type: str = "EXCISE_L1",
        issuing_authority: str = "STATE_EXCISE_BOARD",
    ) -> dict:

        now = datetime.now(timezone.utc)
        record = {
            "id": str(uuid4()),
            "retailer_id": retailer_id,
            "license_number": license_number,
            "license_type": license_type,
            "issuing_authority": issuing_authority,
            "jurisdiction_id": jurisdiction_id,
            "status": "VERIFIED",
            "valid_from": now,
            "valid_until": now + timedelta(days=365),
        }
        self.licenses.setdefault(retailer_id, []).append(record)
        return record

    async def get_eligibility(self, retailer_id: str, jurisdiction_id: str) -> str:
        records = self.licenses.get(retailer_id, [])
        now = datetime.now(timezone.utc)
        for r in records:
            if r["status"] == "VERIFIED" and r["jurisdiction_id"] == jurisdiction_id and r["valid_until"] > now:
                return "ALLOW"
        return "DENY"
