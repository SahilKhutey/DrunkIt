from fastapi import FastAPI
from services.delivery.app.api.assignments import router as assignments_router
from services.delivery.app.api.delivery import router as delivery_router
from services.delivery.app.api.dispatch import router as dispatch_router
from services.delivery.app.api.tracking import router as tracking_router
from services.delivery.app.api.verification import router as verification_router

app = FastAPI(
    title="Delivery & Last-Mile Dispatch Service",
    version="1.0.0",
)

app.include_router(dispatch_router, prefix="/api/v1")
app.include_router(assignments_router, prefix="/api/v1")
app.include_router(tracking_router, prefix="/api/v1")
app.include_router(delivery_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "delivery"}
