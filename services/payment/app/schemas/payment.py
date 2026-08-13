from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):

    order_id: str

    customer_id: str

    amount: int = Field(gt=0)

    currency: str = "INR"

    idempotency_key: str = Field(min_length=10, max_length=200)


class PaymentResponse(BaseModel):

    id: str

    order_id: str

    customer_id: str

    amount: int

    currency: str

    status: str

    provider: str

    provider_payment_id: str | None = None
