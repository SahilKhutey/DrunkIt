from fastapi import FastAPI
from services.compliance.app.api.compliance import router as compliance_router

app = FastAPI(
    title="Compliance & Policy Engine Service",
    version="1.0.0",
)

app.include_router(compliance_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "compliance-service"}
