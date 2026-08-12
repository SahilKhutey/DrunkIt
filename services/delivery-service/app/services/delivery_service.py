"""Delivery service: Dispatch Engine, Driver Geolocation & Proof-of-Delivery OTP."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.db.models import (
    DeliveryAssignment, DeliveryLocationPing, DeliveryMission, ProofOfDelivery,
)
from app.schemas.delivery import (
    DeliveryCompleteRequest, DriverAssignRequest, LocationPingRequest,
    MissionCreate,
)

logger = get_logger(__name__)


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


class DeliveryService:
    """Fulfillment dispatch engine & driver location tracking orchestrator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    async def create_mission(self, payload: MissionCreate) -> tuple[DeliveryMission, str]:
        # Generate 4-digit OTP
        raw_otp = f"{secrets.randbelow(9000) + 1000}"
        otp_hash = _hash_otp(raw_otp)

        code = f"MIS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"

        mission = DeliveryMission(
            mission_code=code,
            order_id=payload.order_id,
            store_id=payload.store_id,
            consumer_id=payload.consumer_id,
            status="QUEUED",
            delivery_otp_hash=otp_hash,
            pickup_address=payload.pickup_address,
            dropoff_address=payload.dropoff_address,
        )
        self.db.add(mission)
        await self.db.commit()
        await self.db.refresh(mission)

        await self._publish("delivery.mission_created", {
            "mission_id": mission.id, "mission_code": mission.mission_code, "order_id": mission.order_id,
        })
        return mission, raw_otp

    async def get_mission(self, mission_id: str) -> DeliveryMission:
        result = await self.db.execute(select(DeliveryMission).where(DeliveryMission.id == mission_id))
        mission = result.scalar_one_or_none()
        if not mission:
            raise NotFoundError(f"Delivery mission {mission_id} not found")
        return mission

    async def assign_driver(self, mission_id: str, payload: DriverAssignRequest) -> DeliveryMission:
        mission = await self.get_mission(mission_id)
        mission.assigned_driver_id = payload.driver_id
        mission.status = "ASSIGNED"

        assign = DeliveryAssignment(
            mission_id=mission.id,
            driver_id=payload.driver_id,
            status="ACCEPTED",
        )
        self.db.add(assign)
        await self.db.commit()
        await self.db.refresh(mission)

        await self._publish("delivery.driver_assigned", {
            "mission_id": mission.id, "driver_id": payload.driver_id,
        })
        return mission

    async def record_ping(self, mission_id: str, payload: LocationPingRequest) -> DeliveryLocationPing:
        mission = await self.get_mission(mission_id)
        if mission.status == "ASSIGNED":
            mission.status = "IN_TRANSIT"

        ping = DeliveryLocationPing(
            mission_id=mission.id,
            driver_id=payload.driver_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        self.db.add(ping)
        await self.db.commit()
        await self.db.refresh(ping)
        return ping

    async def complete_delivery(self, mission_id: str, payload: DeliveryCompleteRequest) -> DeliveryMission:
        mission = await self.get_mission(mission_id)

        # Verify OTP
        if _hash_otp(payload.otp) != mission.delivery_otp_hash:
            raise BadRequestError("Invalid delivery OTP provided by recipient")

        mission.status = "COMPLETED"

        pod = ProofOfDelivery(
            mission_id=mission.id,
            recipient_verified=True,
            verification_method="OTP_SMS",
        )
        self.db.add(pod)
        await self.db.commit()
        await self.db.refresh(mission)

        await self._publish("delivery.completed", {
            "mission_id": mission.id, "order_id": mission.order_id,
        })
        return mission

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-delivery")
            await self.producer.publish("delivery.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
