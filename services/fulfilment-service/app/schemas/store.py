from pydantic import BaseModel

from app.schemas.location import GeoLocation


class Store(BaseModel):

    store_id: str

    retailer_id: str

    name: str

    location: GeoLocation

    service_radius_km: float

    active: bool

    accepting_orders: bool
