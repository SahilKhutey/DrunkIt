from pydantic import BaseModel, Field

from app.schemas.location import GeoLocation


class OrderLine(BaseModel):

    product_id: str

    quantity: int = Field(
        gt=0
    )


class FulfilmentRequest(BaseModel):

    order_id: str

    customer_location: GeoLocation

    items: list[OrderLine]

    requested_store_id: str | None = None


class FulfilmentPlan(BaseModel):

    plan_id: str

    order_id: str

    store_id: str

    retailer_id: str

    items: list[OrderLine]

    status: str

    serviceable: bool

    compliance_status: str = "APPROVED"

    estimated_delivery_minutes: int | None = None
