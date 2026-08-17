from fastapi import FastAPI

from app.api.dispatch import router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "dispatch-engine",
        "version": "0.1.0",
    }


app.include_router(
    router,
    prefix="/api/v1",
)
