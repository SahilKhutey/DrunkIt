from fastapi import FastAPI
from services.security.app.api.actions import router as actions_router
from services.security.app.api.cases import router as cases_router
from services.security.app.api.devices import router as devices_router
from services.security.app.api.risk import router as risk_router
from services.security.app.api.sessions import router as sessions_router
from services.security.app.api.signals import router as signals_router

app = FastAPI(
    title="Fraud, Abuse & Security Operations Engine",
    version="1.0.0",
)

app.include_router(risk_router, prefix="/api/v1")
app.include_router(devices_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(actions_router, prefix="/api/v1")
app.include_router(signals_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "security"}
