from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.api.routes.notification import router as notification_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="FACCP Notification Service", version=settings.service_version)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)
app.include_router(notification_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.service_name}
