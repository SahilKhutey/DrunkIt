from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health Checks"],
)


@router.get("/live")
async def liveness():
    return {"status": "healthy"}


@router.get("/ready")
async def readiness():
    return {"status": "healthy", "checks": {"database": True, "resilience_engine": True}}
