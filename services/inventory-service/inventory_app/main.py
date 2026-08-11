from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(
    title="FACCP Inventory Service",
    description="Real-time Store Stock Reservation & Batch Verification Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InventoryItem(BaseModel):
    store_id: str
    sku: str
    available_stock: int
    reserved_stock: int
    batch_number: str

class ReserveRequest(BaseModel):
    store_id: str
    sku: str
    quantity: int

class ReserveResponse(BaseModel):
    reservation_id: str
    store_id: str
    sku: str
    quantity: int
    success: bool

INVENTORY_DB: Dict[str, Dict[str, InventoryItem]] = {
    "STR-BANGALORE-01": {
        "SKU-WHISKY-SINGLE-MALT-750": InventoryItem(store_id="STR-BANGALORE-01", sku="SKU-WHISKY-SINGLE-MALT-750", available_stock=45, reserved_stock=2, batch_number="BAT-2026-0811"),
        "SKU-GIN-CRAFT-750": InventoryItem(store_id="STR-BANGALORE-01", sku="SKU-GIN-CRAFT-750", available_stock=60, reserved_stock=0, batch_number="BAT-2026-0412"),
        "SKU-CRAFT-BEER-IPA-500": InventoryItem(store_id="STR-BANGALORE-01", sku="SKU-CRAFT-BEER-IPA-500", available_stock=120, reserved_stock=6, batch_number="BAT-2026-0901"),
        "SKU-RED-WINE-CABERNET-750": InventoryItem(store_id="STR-BANGALORE-01", sku="SKU-RED-WINE-CABERNET-750", available_stock=30, reserved_stock=1, batch_number="BAT-2026-0310")
    },
    "STR-MUMBAI-01": {
        "SKU-WHISKY-SINGLE-MALT-750": InventoryItem(store_id="STR-MUMBAI-01", sku="SKU-WHISKY-SINGLE-MALT-750", available_stock=20, reserved_stock=0, batch_number="BAT-2026-1102"),
        "SKU-GIN-CRAFT-750": InventoryItem(store_id="STR-MUMBAI-01", sku="SKU-GIN-CRAFT-750", available_stock=15, reserved_stock=1, batch_number="BAT-2026-1105"),
        "SKU-CRAFT-BEER-IPA-500": InventoryItem(store_id="STR-MUMBAI-01", sku="SKU-CRAFT-BEER-IPA-500", available_stock=80, reserved_stock=0, batch_number="BAT-2026-1110"),
        "SKU-RED-WINE-CABERNET-750": InventoryItem(store_id="STR-MUMBAI-01", sku="SKU-RED-WINE-CABERNET-750", available_stock=25, reserved_stock=2, batch_number="BAT-2026-1112")
    }
}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "inventory-service"}

@app.get("/api/v1/inventory/store/{store_id}", response_model=List[InventoryItem])
def get_store_inventory(store_id: str):
    store_inv = INVENTORY_DB.get(store_id)
    if not store_inv:
        raise HTTPException(status_code=404, detail="Store inventory not found")
    return list(store_inv.values())

@app.post("/api/v1/inventory/reserve", response_model=ReserveResponse)
def reserve_stock(req: ReserveRequest):
    store_inv = INVENTORY_DB.get(req.store_id)
    if not store_inv or req.sku not in store_inv:
        raise HTTPException(status_code=404, detail="SKU not available at store")

    item = store_inv[req.sku]
    if item.available_stock < req.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available for reservation")

    item.available_stock -= req.quantity
    item.reserved_stock += req.quantity

    import uuid
    res_id = f"RES-{uuid.uuid4().hex[:8].upper()}"

    return ReserveResponse(
        reservation_id=res_id,
        store_id=req.store_id,
        sku=req.sku,
        quantity=req.quantity,
        success=True
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
