from datetime import datetime, timezone
from uuid import uuid4

from services.delivery.app.schemas.tracking import LocationUpdate


class TrackingService:

    def __init__(self):
        self.tracking_events: dict[str, list[dict]] = {}
        self.latest_sequences: dict[str, int] = {}

    async def accept_location(self, delivery_id: str, sequence: int) -> bool:
        latest = self.latest_sequences.get(delivery_id)
        if latest is not None and sequence <= latest:
            return False
        return True

    async def record_location(self, delivery_id: str, payload: LocationUpdate) -> dict | None:
        accepted = await self.accept_location(delivery_id, payload.sequence)
        if not accepted:
            return None

        self.latest_sequences[delivery_id] = payload.sequence

        event_id = str(uuid4())
        event = {
            "id": event_id,
            "delivery_id": delivery_id,
            "rider_id": payload.rider_id,
            "event_type": "LOCATION_UPDATE",
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "sequence": payload.sequence,
            "created_at": datetime.now(timezone.utc),
        }

        self.tracking_events.setdefault(delivery_id, []).append(event)
        return event
