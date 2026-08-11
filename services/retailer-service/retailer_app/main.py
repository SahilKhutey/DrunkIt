from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import StoreResponse, ExciseLicenseRecord, SellerTrustLevel, LicenseStatus

app = FastAPI(
    title="FACCP Retailer Domain Service",
    description="Licensed Retail Organization, Store Verification & License Lifecycle Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORES_DB = {
    "STR-BANGALORE-01": StoreResponse(
        store_id="STR-BANGALORE-01",
        organization_name="Apex Premium Spirits Pvt Ltd",
        name="Apex Wines & Spirits - Indiranagar",
        address="100 Feet Road, Indiranagar",
        city="Bengaluru",
        state="Karnataka",
        jurisdiction="IN-KA",
        pincode="560038",
        latitude=12.9716,
        longitude=77.6412,
        trust_level=SellerTrustLevel.S5_FULLY_COMPLIANT,
        active=True,
        license=ExciseLicenseRecord(
            license_id="LIC-KA-2026-9912",
            license_number="KA-EX-CL2-2026-0881",
            license_type="CL-2 Retail Off-Licence",
            issuing_authority="Karnataka State Excise Department",
            jurisdiction="IN-KA",
            holder_name="Apex Premium Spirits Pvt Ltd",
            store_id="STR-BANGALORE-01",
            valid_from="2025-04-01",
            valid_until="2027-03-31",
            permitted_categories=["BEER", "WINE", "SPIRITS", "RTD"],
            status=LicenseStatus.ACTIVE
        )
    ),
    "STR-MUMBAI-01": StoreResponse(
        store_id="STR-MUMBAI-01",
        organization_name="Royal Cellars Retail LLC",
        name="Royal Cellars - Bandra West",
        address="Hill Road, Bandra West",
        city="Mumbai",
        state="Maharashtra",
        jurisdiction="IN-MH",
        pincode="400050",
        latitude=19.0596,
        longitude=72.8295,
        trust_level=SellerTrustLevel.S5_FULLY_COMPLIANT,
        active=True,
        license=ExciseLicenseRecord(
            license_id="LIC-MH-2026-4410",
            license_number="MH-FL1-2026-5521",
            license_type="FL-I Wine & Spirits Licence",
            issuing_authority="Maharashtra State Excise Department",
            jurisdiction="IN-MH",
            holder_name="Royal Cellars Retail LLC",
            store_id="STR-MUMBAI-01",
            valid_from="2025-04-01",
            valid_until="2027-03-31",
            permitted_categories=["BEER", "WINE", "SPIRITS"],
            status=LicenseStatus.ACTIVE
        )
    )
}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "retailer-service"}

@app.get("/api/v1/stores", response_model=List[StoreResponse])
def list_stores(jurisdiction: str = "IN-KA"):
    return [s for s in STORES_DB.values() if s.jurisdiction == jurisdiction]

@app.get("/api/v1/stores/{store_id}", response_model=StoreResponse)
def get_store(store_id: str):
    store = STORES_DB.get(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store record not found")
    return store

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
