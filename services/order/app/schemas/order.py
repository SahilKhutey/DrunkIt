from pydantic import BaseModel


class OrderResponse(BaseModel):

    id: str

    customer_id: str

    store_id: str

    status: str

    subtotal: int

    delivery_fee: int

    taxes: int

    discount: int

    total: int

    currency: str = "INR"


class OrderCancellationRequest(BaseModel):

    reason: str = "CUSTOMER_CANCELLED"
