from fastapi import FastAPI

from app.api.drivers import router as driver_router
from app.api.location import router as location_router
from app.api.internal import router as internal_router

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "driver-service",
        "version": "0.1.0",
    }


app.include_router(
    driver_router,
    prefix=settings.api_prefix,
)

app.include_router(
    location_router,
    prefix=settings.api_prefix,
)

app.include_router(
    internal_router,
    prefix=settings.api_prefix,
)
