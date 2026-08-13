from pydantic import BaseModel, Field


class StockReceipt(BaseModel):

    store_id: str

    sku_id: str

    quantity: int = Field(gt=0)

    reference_id: str | None = None

    idempotency_key: str


class StockAdjustment(BaseModel):

    store_id: str

    sku_id: str

    delta: int

    reason: str

    idempotency_key: str
