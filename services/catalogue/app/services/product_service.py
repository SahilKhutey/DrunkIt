from datetime import datetime, timezone
from uuid import uuid4

from services.catalogue.app.schemas.product import ProductCreate


class ProductService:

    def __init__(self, repository=None):
        self.repository = repository or {}

    async def create(
        self,
        data: ProductCreate,
    ):
        if data.product_code in self.repository:
            raise ValueError("Product code already exists")

        now = datetime.now(timezone.utc)
        product_obj = {
            "id": str(uuid4()),
            "product_code": data.product_code,
            "name": data.name,
            "description": data.description,
            "brand_id": data.brand_id,
            "category": data.category,
            "regulated": data.regulated,
            "active": True,
            "created_at": now,
            "updated_at": now,
        }

        self.repository[data.product_code] = product_obj
        return product_obj
