"""Async Repository for Consumer Verification entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.enums import VerificationMethod, VerificationStatus
from ..models.verification import ConsumerVerification


class VerificationRepository:
    """Repository handling consumer verification operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, consumer_id: str | uuid.UUID) -> ConsumerVerification | None:
        """Fetch verification record by consumer_id."""
        cid_str = str(consumer_id)
        result = await self.session.execute(
            select(ConsumerVerification).where(ConsumerVerification.consumer_id == cid_str)
        )
        return result.scalar_one_or_none()

    async def mark_verified(
        self,
        consumer_id: str | uuid.UUID,
        *,
        method: VerificationMethod,
        provider_reference: str | None = None,
        verified_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> ConsumerVerification:
        """Mark consumer as verified and record verification details."""
        cid_str = str(consumer_id)
        verification = await self.get(cid_str)
        v_time = verified_at or datetime.now(timezone.utc)

        if verification is None:
            verification = ConsumerVerification(
                consumer_id=cid_str,
                status=VerificationStatus.VERIFIED,
                method=method,
                provider_reference=provider_reference,
                verified_at=v_time,
                expires_at=expires_at,
            )
            self.session.add(verification)
        else:
            verification.status = VerificationStatus.VERIFIED
            verification.method = method
            verification.provider_reference = provider_reference
            verification.verified_at = v_time
            verification.expires_at = expires_at

        await self.session.flush()
        return verification
