from pydantic import BaseModel


class SKUCreate(BaseModel):

    product_id: str

    sku_code: str

    barcode: str | None = None

    volume_ml: int | None = None

    packaging_type: str | None = None

    strength_value: float | None = None

    strength_unit: str | None = None
