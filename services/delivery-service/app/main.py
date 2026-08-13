from fastapi import FastAPI

from app.api.delivery import router as delivery_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "delivery-engine",
        "version": "0.1.0",
    }


app.include_router(
    delivery_router,
    prefix=settings.api_prefix,
)
