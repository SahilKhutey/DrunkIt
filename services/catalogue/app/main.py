from fastapi import FastAPI
from services.catalogue.app.api.listings import router as listings_router
from services.catalogue.app.api.products import router as products_router
from services.catalogue.app.api.skus import router as skus_router

app = FastAPI(
    title="Regulatory Product Catalogue & SKU Intelligence Service",
    version="1.0.0",
)

app.include_router(products_router)
app.include_router(skus_router)
app.include_router(listings_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "catalogue-service"}
