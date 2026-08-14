"""Consumer Verification API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.config.settings import get_settings
from faccp_platform.database.session import get_db_session
from faccp_platform.security.principal import Principal
from ..deps import current_principal
from ...domain.enums import VerificationMethod, VerificationStatus
from ...repositories.consumer import ConsumerRepository
from ...schemas.verification import VerificationResult
from ...services.consumer_service import ConsumerService
from ...services.verification_service import VerificationService

router = APIRouter(prefix="/consumers", tags=["verification"])


@router.get(
    "/{consumer_id}/verification",
    response_model=VerificationResult,
)
async def get_verification(
    consumer_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Retrieve consumer verification status."""
    consumer_repo = ConsumerRepository(session)
    consumer = await consumer_repo.get(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found",
        )

    if (
        str(principal.user_id) != str(consumer.identity_id)
        and not principal.has_permission("consumer:verification:read")
        and not principal.has_permission("consumers:read:any")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    verification_service = VerificationService(session)
    verification = await verification_service.get(consumer_id)

    if verification is None:
        return VerificationResult(status=VerificationStatus.NOT_STARTED)

    return VerificationResult(
        status=verification.status,
        provider_reference=verification.provider_reference,
        verified_at=verification.verified_at,
        expires_at=verification.expires_at,
    )


@router.post(
    "/{consumer_id}/verification/mock",
    response_model=VerificationResult,
)
async def mock_verification(
    consumer_id: uuid.UUID,
    method: VerificationMethod,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Development-only mock verification endpoint."""
    settings = get_settings()
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mock verification is only enabled in development mode",
        )

    consumer_repo = ConsumerRepository(session)
    consumer = await consumer_repo.get(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found",
        )

    verification_service = VerificationService(session)
    consumer_service = ConsumerService(consumer_repo, session=session)

    verification = await verification_service.mark_verified(
        consumer_id,
        method=method,
        provider_reference="mock-provider-ref-001",
    )
    await consumer_service.activate(consumer_id)
    await session.commit()
    await session.refresh(verification)

    return VerificationResult(
        status=verification.status,
        provider_reference=verification.provider_reference,
        verified_at=verification.verified_at,
        expires_at=verification.expires_at,
    )
