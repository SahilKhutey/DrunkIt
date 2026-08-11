from typing import Annotated
from fastapi import APIRouter, Depends, Header
from faccp_common.dto import APIResponse
from faccp_common.exceptions import UnauthorizedError
from faccp_common.security import decode_token
from app.api.dependencies import get_payment_service
from app.config import get_settings
from app.schemas.payment import (
    AuthorizeRequest, CreateIntentRequest, IntentResponse, RefundRequest,
    RefundResponse, TransactionResponse, WebhookPayload,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
settings = get_settings()


def _auth(authorization: str | None) -> dict:
    if not authorization:
        raise UnauthorizedError("Authentication required")
    try:
        token = authorization.replace("Bearer ", "").strip()
        return decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience, expected_type="access"
        )
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e


@router.post("/intents", status_code=201)
async def create_intent(
    payload: CreateIntentRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[IntentResponse]:
    claims = _auth(authorization)
    intent = await service.create_intent(payload, claims.get("sub", ""))
    return APIResponse(data=intent)


@router.post("/intents/{intent_id}/authorize")
async def authorize(
    intent_id: str,
    payload: AuthorizeRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[TransactionResponse]:
    claims = _auth(authorization)
    txn = await service.authorize(intent_id, payload.provider_payment_id, claims.get("sub", ""))
    return APIResponse(data=txn)


@router.post("/intents/{intent_id}/capture")
async def capture(
    intent_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[TransactionResponse]:
    claims = _auth(authorization)
    txn = await service.capture(intent_id, claims.get("sub", ""))
    return APIResponse(data=txn)


@router.post("/refunds", status_code=201)
async def create_refund(
    payload: RefundRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[RefundResponse]:
    claims = _auth(authorization)
    refund = await service.create_refund(payload, claims.get("sub", ""), claims.get("primary_role", ""))
    return APIResponse(data=refund)


@router.post("/refunds/{refund_id}/approve")
async def approve_refund(
    refund_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[RefundResponse]:
    claims = _auth(authorization)
    refund = await service.approve_refund(refund_id, claims.get("sub", ""))
    return APIResponse(data=refund)


@router.post("/webhooks/{provider}", include_in_schema=False)
async def webhook(
    provider: str,
    payload: WebhookPayload,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    x_signature: Annotated[str | None, Header()] = None,
) -> dict:
    return await service.process_webhook(provider, payload, x_signature)
