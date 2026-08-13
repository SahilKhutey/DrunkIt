from datetime import datetime
from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):

    rider_id: str

    latitude: float = Field(ge=-90, le=90)

    longitude: float = Field(ge=-180, le=180)

    timestamp: datetime

    sequence: int = Field(ge=0)


class TrackingEventResponse(BaseModel):

    id: str

    delivery_id: str

    event_type: str

    latitude: float | None = None

    longitude: float | None = None
