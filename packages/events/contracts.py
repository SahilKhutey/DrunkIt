from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventEnvelope(BaseModel):

    event_id: UUID

    event_type: str

    aggregate_type: str

    aggregate_id: str

    occurred_at: datetime

    version: int = 1

    payload: dict
