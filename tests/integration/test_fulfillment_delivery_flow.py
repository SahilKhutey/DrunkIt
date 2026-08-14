"""Integration tests for end-to-end fulfillment, inventory, delivery, and verification flows."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from services.fulfillment.app.domain.enums import DeliveryStatus, FulfillmentStatus, VerificationStatus
from services.fulfillment.app.models.courier import Courier
from services.fulfillment.app.services.delivery_service import DeliveryService
from services.fulfillment.app.services.fulfillment_service import FulfillmentService
from services.fulfillment.app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_end_to_end_fulfillment_delivery_flow():
    """Verify complete flow from payment captured -> inventory reservation -> pick/pack -> delivery assignment -> arrived -> verification pass -> delivered."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    oid = str(uuid.uuid4())
    wid = str(uuid.uuid4())
    pid = str(uuid.uuid4())

    async with session_factory() as session:
        # Create active courier
        courier = Courier(name="Courier Alpha", phone="+919876543210", active=True, latitude=12.97, longitude=77.59)
        session.add(courier)
        await session.commit()

    async with session_factory() as session:
        fulfil_svc = FulfillmentService(session)
        deliv_svc = DeliveryService(session)
        verif_svc = VerificationService(session)

        # 1. Create fulfillment + reserve stock
        fulfilment = await fulfil_svc.create_fulfillment(oid, wid, pid, quantity=2)
        assert fulfilment.status == FulfillmentStatus.RESERVED

        # 2. Pick & Pack
        await fulfil_svc.start_picking(fulfilment)
        assert fulfilment.status == FulfillmentStatus.PICKING
        await fulfil_svc.pack(fulfilment)
        assert fulfilment.status == FulfillmentStatus.PACKING
        await fulfil_svc.mark_ready(fulfilment)
        assert fulfilment.status == FulfillmentStatus.READY_FOR_PICKUP

        # 3. Create delivery & Assign Courier
        deliv = await deliv_svc.create_delivery(oid, fulfilment.id)
        assert deliv.status == DeliveryStatus.CREATED
        await deliv_svc.assign_courier(deliv)
        assert deliv.status == DeliveryStatus.ASSIGNED
        assert deliv.courier_id is not None

        # 4. Pickup & In Transit & Arrived
        await deliv_svc.pickup(deliv)
        assert deliv.status == DeliveryStatus.IN_TRANSIT
        await deliv_svc.arrived(deliv)
        assert deliv.status == DeliveryStatus.VERIFICATION_PENDING

        # 5. Verification Handoff
        verif = await verif_svc.start(deliv.id)
        assert verif.status == VerificationStatus.PENDING
        await verif_svc.complete(verif, passed=True, method="Aadhaar_OTP", reference="REF-999-PASS")
        assert verif.status == VerificationStatus.PASSED

        # 6. Complete Delivery
        res = await deliv_svc.complete_delivery(deliv, verif)
        assert res.status == DeliveryStatus.DELIVERED
        assert res.delivered_at is not None

        await session.commit()

    await engine.dispose()
