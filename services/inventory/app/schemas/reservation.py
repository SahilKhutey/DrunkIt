from pydantic import BaseModel, Field


class ReservationCreate(BaseModel):

    order_id: str

    store_id: str

    sku_id: str

    quantity: int = Field(gt=0)

    idempotency_key: str
