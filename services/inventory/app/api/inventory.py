from fastapi import APIRouter, HTTPException
from services.inventory.app.schemas.inventory import StockAdjustment, StockReceipt
from services.inventory.app.services.inventory_service import InventoryService

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)

inventory_service = InventoryService()


@router.get("/{store_id}/{sku_id}")
async def get_inventory(
    store_id: str,
    sku_id: str,
):
    available = await inventory_service.get_available(store_id, sku_id)
    return {
        "store_id": store_id,
        "sku_id": sku_id,
        "available": available,
    }


@router.post("/receipt")
async def receive_stock(payload: StockReceipt):
    return await inventory_service.receive_stock(payload)


@router.post("/adjust")
async def adjust_stock(payload: StockAdjustment):
    try:
        return await inventory_service.adjust(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
