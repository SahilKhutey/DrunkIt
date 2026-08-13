from pydantic import BaseModel


class DeliveryCreate(BaseModel):

    order_id: str

    retailer_id: str

    delivery_address_id: str

    regulated_product: bool = True


class DeliveryResponse(BaseModel):

    id: str

    order_id: str

    status: str

    eta_seconds: int | None = None

    verification_required: bool


class DeliveryFailureRequest(BaseModel):

    reason: str

    notes: str | None = None
