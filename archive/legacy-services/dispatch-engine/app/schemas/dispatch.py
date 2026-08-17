from datetime import datetime

from pydantic import BaseModel, Field


class Location(BaseModel):

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )


class DispatchRequest(BaseModel):

    delivery_id: str

    pickup_location: Location

    required_vehicle_type: str | None = None


class DriverCandidate(BaseModel):

    driver_id: str

    vehicle_type: str

    latitude: float | None

    longitude: float | None


class DriverScore(BaseModel):

    driver_id: str

    distance_km: float

    estimated_pickup_minutes: float

    score: float


class DispatchResponse(BaseModel):

    delivery_id: str

    driver_id: str

    status: str

    assigned_at: datetime | None = None
