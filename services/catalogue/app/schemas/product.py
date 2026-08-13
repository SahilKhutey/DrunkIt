from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    product_code: str = Field(min_length=2, max_length=100)

    name: str = Field(min_length=1, max_length=255)

    description: str | None = None

    brand_id: str

    category: str

    regulated: bool = False
