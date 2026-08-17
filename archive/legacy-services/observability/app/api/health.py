from fastapi import APIRouter
from services.observability.app.collectors.health_collectors import (
    database_health,
    redis_health,
)

router = APIRouter(
    prefix="/health",
    tags=["Health Checks"],
)


@router.get("/live")
async def liveness():
    return {"status": "healthy"}


@router.get("/ready")
async def readiness():
    checks = {
        "database": await database_health(),
        "redis": await redis_health(),
    }
    healthy = all(checks.values())
    return {
        "status": "healthy" if healthy else "unhealthy",
        "checks": checks,
    }
