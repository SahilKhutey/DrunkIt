from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="FACCP Catalog Service",
    description="Alcoholic Beverage SKU Taxonomy & Regulatory Product Classification Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductSKU(BaseModel):
    sku: str
    name: str
    brand: str
    category: str  # BEER, WINE, SPIRITS, RTD
    abv: float
    volume_ml: int
    country_of_origin: str
    image_url: str
    base_price: float
    tax_rate_percent: float

CATALOG_DB = [
    ProductSKU(
        sku="SKU-WHISKY-SINGLE-MALT-750",
        name="Amrut Fusion Single Malt Indian Whisky",
        brand="Amrut",
        category="SPIRITS",
        abv=50.0,
        volume_ml=750,
        country_of_origin="India",
        image_url="https://images.unsplash.com/photo-1527281400683-1aae777175f8?w=500&auto=format&fit=crop",
        base_price=4200.0,
        tax_rate_percent=18.0
    ),
    ProductSKU(
        sku="SKU-GIN-CRAFT-750",
        name="Stranger & Sons Trading Company Gin",
        brand="Stranger & Sons",
        category="SPIRITS",
        abv=42.8,
        volume_ml=750,
        country_of_origin="India",
        image_url="https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500&auto=format&fit=crop",
        base_price=2800.0,
        tax_rate_percent=18.0
    ),
    ProductSKU(
        sku="SKU-CRAFT-BEER-IPA-500",
        name="BIRA 91 Boom Super Strong Craft Beer",
        brand="Bira 91",
        category="BEER",
        abv=7.0,
        volume_ml=500,
        country_of_origin="India",
        image_url="https://images.unsplash.com/photo-1608270586620-248524c67de9?w=500&auto=format&fit=crop",
        base_price=180.0,
        tax_rate_percent=12.0
    ),
    ProductSKU(
        sku="SKU-RED-WINE-CABERNET-750",
        name="Sula Rasa Cabernet Sauvignon Wine",
        brand="Sula Vineyards",
        category="WINE",
        abv=13.5,
        volume_ml=750,
        country_of_origin="India",
        image_url="https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=500&auto=format&fit=crop",
        base_price=1650.0,
        tax_rate_percent=18.0
    )
]

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "catalog-service"}

@app.get("/api/v1/catalog/products", response_model=List[ProductSKU])
def get_products(category: Optional[str] = None):
    if category:
        return [p for p in CATALOG_DB if p.category.upper() == category.upper()]
    return CATALOG_DB

@app.get("/api/v1/catalog/products/{sku}", response_model=ProductSKU)
def get_product(sku: str):
    for p in CATALOG_DB:
        if p.sku == sku:
            return p
    raise HTTPException(status_code=404, detail="Product SKU not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
