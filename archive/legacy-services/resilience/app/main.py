from fastapi import FastAPI
from services.resilience.app.api.backups import router as backups_router
from services.resilience.app.api.continuity import router as continuity_router
from services.resilience.app.api.failover import router as failover_router
from services.resilience.app.api.health import router as health_router
from services.resilience.app.api.recovery import router as recovery_router

app = FastAPI(
    title="Disaster Recovery, Resilience & Business Continuity Engine",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(backups_router)
app.include_router(recovery_router)
app.include_router(failover_router)
app.include_router(continuity_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "resilience"}
