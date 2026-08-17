from fastapi import APIRouter
from services.catalogue.app.schemas.sku import SKUCreate
from services.catalogue.app.services.sku_service import SKUService

router = APIRouter(
    prefix="/admin/skus",
    tags=["Admin SKUs"],
)

sku_service = SKUService()


@router.post("")
async def create_sku(payload: SKUCreate):
    return await sku_service.create(payload)
