from fastapi import APIRouter
from services.payment.app.api.payments import payment_service
from services.payment.app.services.reconciliation_service import ReconciliationService

router = APIRouter(
    prefix="/reconciliation",
    tags=["Reconciliation"],
)

reconciliation_service = ReconciliationService(payment_service=payment_service)


@router.post("")
async def reconcile(provider_transactions: list[dict]):
    return await reconciliation_service.reconcile(provider_transactions)
