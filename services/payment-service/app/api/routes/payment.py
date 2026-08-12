"""Payment API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_payment_service
from app.schemas.payment import (
    LedgerEntryResponse, PaymentCaptureRequest, PaymentIntentCreate,
    PaymentIntentResponse, PaymentRefundRequest,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["Financial Engine"])


@router.post("/intents", response_model=SuccessResponse[PaymentIntentResponse], status_code=201)
async def create_intent(
    payload: PaymentIntentCreate,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> SuccessResponse[PaymentIntentResponse]:
    intent = await service.create_intent(payload)
    return SuccessResponse(data=PaymentIntentResponse(
        id=intent.id, order_id=intent.order_id, consumer_id=intent.consumer_id,
        amount_inr=intent.amount_inr, currency=intent.currency, status=intent.status,
        gateway_provider=intent.gateway_provider,
        gateway_transaction_id=intent.gateway_transaction_id, created_at=intent.created_at,
    ), message="Payment intent created")


@router.get("/intents/{intent_id}", response_model=SuccessResponse[PaymentIntentResponse])
async def get_intent(
    intent_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> SuccessResponse[PaymentIntentResponse]:
    intent = await service.get_intent(intent_id)
    return SuccessResponse(data=PaymentIntentResponse(
        id=intent.id, order_id=intent.order_id, consumer_id=intent.consumer_id,
        amount_inr=intent.amount_inr, currency=intent.currency, status=intent.status,
        gateway_provider=intent.gateway_provider,
        gateway_transaction_id=intent.gateway_transaction_id, created_at=intent.created_at,
    ))


@router.post("/intents/{intent_id}/capture", response_model=SuccessResponse[PaymentIntentResponse])
async def capture_payment(
    intent_id: str,
    payload: PaymentCaptureRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> SuccessResponse[PaymentIntentResponse]:
    intent = await service.capture_payment(intent_id, payload)
    return SuccessResponse(data=PaymentIntentResponse(
        id=intent.id, order_id=intent.order_id, consumer_id=intent.consumer_id,
        amount_inr=intent.amount_inr, currency=intent.currency, status=intent.status,
        gateway_provider=intent.gateway_provider,
        gateway_transaction_id=intent.gateway_transaction_id, created_at=intent.created_at,
    ), message="Payment captured & ledger entry posted")


@router.post("/intents/{intent_id}/refund", response_model=SuccessResponse[PaymentIntentResponse])
async def refund_payment(
    intent_id: str,
    payload: PaymentRefundRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> SuccessResponse[PaymentIntentResponse]:
    intent = await service.refund_payment(intent_id, payload)
    return SuccessResponse(data=PaymentIntentResponse(
        id=intent.id, order_id=intent.order_id, consumer_id=intent.consumer_id,
        amount_inr=intent.amount_inr, currency=intent.currency, status=intent.status,
        gateway_provider=intent.gateway_provider,
        gateway_transaction_id=intent.gateway_transaction_id, created_at=intent.created_at,
    ), message="Payment refunded & reversal ledger entry posted")


@router.get("/ledger", response_model=SuccessResponse[list[LedgerEntryResponse]])
async def list_ledger_entries(
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> SuccessResponse[list[LedgerEntryResponse]]:
    entries = await service.list_ledger_entries()
    return SuccessResponse(data=[LedgerEntryResponse(
        id=e.id, entry_id=e.entry_id, account_debit=e.account_debit,
        account_credit=e.account_credit, amount_inr=e.amount_inr,
        reference_id=e.reference_id, created_at=e.created_at,
    ) for e in entries])
