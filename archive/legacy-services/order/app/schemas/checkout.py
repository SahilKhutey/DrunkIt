from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):

    cart_id: str

    customer_id: str

    store_id: str

    idempotency_key: str = Field(min_length=10, max_length=200)


class CheckoutResponse(BaseModel):

    order_id: str

    status: str

    subtotal: int

    taxes: int

    delivery_fee: int

    discount: int

    total: int

    currency: str = "INR"
