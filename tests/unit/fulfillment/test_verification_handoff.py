"""Unit tests for delivery verification handoff security."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from services.fulfillment.app.domain.enums import DeliveryStatus, VerificationStatus
from services.fulfillment.app.services.delivery_service import DeliveryService
from services.fulfillment.app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_delivery_requires_verification_pass():
    """Verify that a failed verification prevents delivery completion."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        deliv_svc = DeliveryService(session)
        verif_svc = VerificationService(session)

        oid = str(uuid.uuid4())
        fid = str(uuid.uuid4())

        deliv = await deliv_svc.create_delivery(oid, fid)
        deliv.status = DeliveryStatus.VERIFICATION_PENDING

        verif = await verif_svc.start(deliv.id)
        await verif_svc.complete(verif, passed=False, method="Govt_ID_OTP", reference="REF-101-FAIL")

        # Complete delivery should fail due to failed verification
        with pytest.raises(ValueError, match="Delivery verification failed"):
            await deliv_svc.complete_delivery(deliv, verif)

    await engine.dispose()


@pytest.mark.asyncio
async def test_delivery_completes_after_verification_pass():
    """Verify that a passed verification allows successful delivery completion."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        deliv_svc = DeliveryService(session)
        verif_svc = VerificationService(session)

        oid = str(uuid.uuid4())
        fid = str(uuid.uuid4())

        deliv = await deliv_svc.create_delivery(oid, fid)
        deliv.status = DeliveryStatus.VERIFICATION_PENDING

        verif = await verif_svc.start(deliv.id)
        await verif_svc.complete(verif, passed=True, method="Govt_ID_OTP", reference="REF-101-PASS")

        res = await deliv_svc.complete_delivery(deliv, verif)
        assert res.status == DeliveryStatus.DELIVERED
        assert res.delivered_at is not None

    await engine.dispose()
