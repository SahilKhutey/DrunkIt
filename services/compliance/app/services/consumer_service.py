from datetime import datetime, timedelta, timezone
from uuid import uuid4


class ConsumerService:

    def __init__(self):
        self.verifications: dict[str, dict] = {}

    async def verify_consumer(self, consumer_id: str, provider: str = "ID_GOV_VERIFY") -> dict:
        now = datetime.now(timezone.utc)
        record = {
            "id": str(uuid4()),
            "consumer_id": consumer_id,
            "status": "VERIFIED",
            "provider": provider,
            "verification_reference": f"vrf_ref_{consumer_id}",
            "verified_at": now,
            "expires_at": now + timedelta(days=365),
        }
        self.verifications[consumer_id] = record
        return record

    async def get_verification(self, consumer_id: str) -> dict | None:
        return self.verifications.get(consumer_id)
