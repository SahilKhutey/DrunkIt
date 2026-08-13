from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):

    sku_id: str

    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):

    quantity: int = Field(gt=0)
