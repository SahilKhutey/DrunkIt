from fastapi import FastAPI
from services.payment.app.api.payments import router as payments_router
from services.payment.app.api.reconciliation import router as reconciliation_router
from services.payment.app.api.refunds import router as refunds_router
from services.payment.app.api.transactions import router as transactions_router
from services.payment.app.api.webhooks import router as webhooks_router

app = FastAPI(
    title="Payment & Financial Transaction Engine Service",
    version="1.0.0",
)

app.include_router(payments_router, prefix="/api/v1")
app.include_router(refunds_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(reconciliation_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "payment"}
