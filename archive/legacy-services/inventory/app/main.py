from fastapi import FastAPI
from services.inventory.app.api.fulfilment import router as fulfilment_router
from services.inventory.app.api.inventory import router as inventory_router
from services.inventory.app.api.reservations import router as reservations_router

app = FastAPI(
    title="Inventory & Store Fulfilment Engine Service",
    version="1.0.0",
)

app.include_router(inventory_router)
app.include_router(reservations_router)
app.include_router(fulfilment_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "inventory-fulfilment-service"}
