from fastapi import FastAPI
from services.observability.app.api.alerts import router as alerts_router
from services.observability.app.api.health import router as health_router
from services.observability.app.api.incidents import router as incidents_router
from services.observability.app.api.logs import router as logs_router
from services.observability.app.api.metrics import router as metrics_router
from services.observability.app.api.services import router as services_router
from services.observability.app.api.traces import router as traces_router

app = FastAPI(
    title="Observability, Monitoring & Reliability Engine",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(logs_router)
app.include_router(traces_router)
app.include_router(alerts_router)
app.include_router(incidents_router)
app.include_router(services_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "observability"}
