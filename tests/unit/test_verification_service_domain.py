"""Unit test for Consumer Verification domain service."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from faccp_platform.database.base import Base
from services.consumer.app.domain.enums import VerificationMethod, VerificationStatus
from services.consumer.app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_verification_result():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    consumer_id = uuid.uuid4()

    async with sessionmaker() as session:
        service = VerificationService(session)
        result = await service.mark_verified(
            consumer_id=consumer_id,
            method=VerificationMethod.MANUAL,
            provider_reference="test-provider-001",
        )
        assert result.status == VerificationStatus.VERIFIED
        assert result.provider_reference == "test-provider-001"

    await engine.dispose()
