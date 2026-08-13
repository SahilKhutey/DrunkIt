from pydantic import BaseModel

from app.schemas.location import GeoLocation


class ServiceabilityRequest(BaseModel):

    customer_location: GeoLocation

    city_id: str | None = None

    requested_store_id: str | None = None


class ServiceabilityResponse(BaseModel):

    serviceable: bool

    reason: str | None = None

    zone_id: str | None = None

    available_store_count: int = 0
