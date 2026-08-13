from fastapi import FastAPI

from app.api.fulfilment import router as fulfilment_router
from app.api.serviceability import router as serviceability_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "fulfilment-service",
        "version": "0.1.0",
    }


app.include_router(
    serviceability_router,
    prefix="/api/v1",
)

app.include_router(
    fulfilment_router,
    prefix="/api/v1",
)
