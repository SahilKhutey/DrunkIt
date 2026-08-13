from datetime import datetime, timezone
from uuid import uuid4

from services.catalogue.app.schemas.sku import SKUCreate


class SKUService:

    def __init__(self, repository=None):
        self.repository = repository or {}

    async def create(
        self,
        data: SKUCreate,
    ):
        if data.sku_code in self.repository:
            raise ValueError("SKU already exists")

        now = datetime.now(timezone.utc)
        sku_obj = {
            "id": str(uuid4()),
            "product_id": data.product_id,
            "sku_code": data.sku_code,
            "barcode": data.barcode,
            "volume_ml": data.volume_ml,
            "packaging_type": data.packaging_type,
            "strength_value": data.strength_value,
            "strength_unit": data.strength_unit,
            "active": True,
            "created_at": now,
        }

        self.repository[data.sku_code] = sku_obj
        return sku_obj
