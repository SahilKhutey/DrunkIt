"""Payment REST API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.config.settings import get_settings
from faccp_platform.database.session import get_db_session
from ...repositories.payment import PaymentRepository
from ...schemas.payment import CapturePaymentRequest, CreatePaymentRequest, PaymentResponse
from ...services.mock_provider import MockPaymentProvider
from ...services.payment_service import PaymentService
from ...services.risk_client import RiskClient

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    request: CreatePaymentRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create risk-gated, idempotent payment intent."""
    settings = get_settings()
    risk_url = getattr(settings, "RISK_SERVICE_URL", "http://localhost:8012")
    risk_client = RiskClient(base_url=risk_url)
    provider = MockPaymentProvider()
    service = PaymentService(session=session, provider=provider, risk_client=risk_client)

    try:
        payment, provider_res = await service.create_payment(request)
        await session.commit()
        await session.refresh(payment)

        resp = PaymentResponse.model_validate(payment)
        resp.client_secret = provider_res.client_secret
        return resp
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.post(
    "/{payment_id}/capture",
    response_model=PaymentResponse,
)
async def capture_payment(
    payment_id: uuid.UUID,
    request: CapturePaymentRequest = CapturePaymentRequest(),
    session: AsyncSession = Depends(get_db_session),
):
    """Capture authorized payment."""
    provider = MockPaymentProvider()
    service = PaymentService(session=session, provider=provider)

    try:
        payment = await service.capture_payment(payment_id, amount=request.amount)
        await session.commit()
        await session.refresh(payment)
        return PaymentResponse.model_validate(payment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def get_payment(
    payment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch payment by payment_id."""
    repo = PaymentRepository(session)
    payment = await repo.get(payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return PaymentResponse.model_validate(payment)
