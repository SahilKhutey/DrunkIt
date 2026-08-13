from fastapi import FastAPI
from services.compliance.app.api.audits import router as audits_router
from services.compliance.app.api.consumer import router as consumer_router
from services.compliance.app.api.decisions import router as decisions_router
from services.compliance.app.api.policies import router as policies_router
from services.compliance.app.api.retailer import router as retailer_router
from services.compliance.app.api.rider import router as rider_router

app = FastAPI(
    title="Compliance & Trust Engine",
    version="1.0.0",
)

app.include_router(decisions_router, prefix="/api/v1")
app.include_router(consumer_router, prefix="/api/v1")
app.include_router(retailer_router, prefix="/api/v1")
app.include_router(rider_router, prefix="/api/v1")
app.include_router(policies_router, prefix="/api/v1")
app.include_router(audits_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "compliance"}
