from fastapi import APIRouter
from services.payment.app.api.payments import payment_service

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions & Ledger"],
)


@router.get("")
async def list_transactions():
    return list(payment_service.ledger.transactions.values())
