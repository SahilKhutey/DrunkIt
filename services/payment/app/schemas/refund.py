from pydantic import BaseModel, Field


class RefundRequest(BaseModel):

    payment_id: str

    amount: int = Field(gt=0)

    reason: str = "CUSTOMER_REQUEST"

    idempotency_key: str = Field(min_length=10, max_length=200)


class RefundResponse(BaseModel):

    id: str

    payment_id: str

    order_id: str

    amount: int

    status: str

    provider_refund_id: str | None = None
