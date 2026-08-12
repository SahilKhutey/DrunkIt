"""Consumer service: Profile management, Delivery Address Book, Age Verification workflows."""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import AgeVerificationRecord, ConsumerProfile, DeliveryAddress
from app.schemas.consumer import (
    AddressCreate, AgeVerificationSubmit, ConsumerProfileCreate,
)

logger = get_logger(__name__)
settings = get_settings()


class ConsumerService:
    """Consumer profile & address book orchestrator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # PROFILE MANAGEMENT
    # ============================================================
    async def create_profile(self, payload: ConsumerProfileCreate) -> ConsumerProfile:
        existing = await self.get_profile_by_user_id(payload.user_id)
        if existing:
            raise ConflictError(f"Consumer profile for user_id {payload.user_id} already exists")

        profile = ConsumerProfile(
            user_id=payload.user_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            display_name=payload.display_name or f"{payload.first_name} {payload.last_name[0]}.",
            date_of_birth=payload.date_of_birth,
            consumer_level="C1_REGISTERED",
            primary_jurisdiction=payload.primary_jurisdiction,
            preferred_language=payload.preferred_language,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        await self._publish("consumer.created", {
            "consumer_id": profile.id, "user_id": profile.user_id,
            "level": profile.consumer_level,
        })
        return profile

    async def get_profile(self, consumer_id: str) -> ConsumerProfile:
        result = await self.db.execute(select(ConsumerProfile).where(ConsumerProfile.id == consumer_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(f"Consumer profile {consumer_id} not found")
        return profile

    async def get_profile_by_user_id(self, user_id: str) -> ConsumerProfile | None:
        result = await self.db.execute(select(ConsumerProfile).where(ConsumerProfile.user_id == user_id))
        return result.scalar_one_or_none()

    # ============================================================
    # ADDRESS BOOK MANAGEMENT
    # ============================================================
    async def add_address(self, consumer_id: str, payload: AddressCreate) -> DeliveryAddress:
        profile = await self.get_profile(consumer_id)

        # Enforce address limit
        existing_addresses = await self.list_addresses(consumer_id)
        if len(existing_addresses) >= settings.max_addresses_per_consumer:
            raise BadRequestError(f"Address limit of {settings.max_addresses_per_consumer} reached")

        # If first address, auto-set default
        is_default = payload.is_default or len(existing_addresses) == 0

        if is_default and len(existing_addresses) > 0:
            await self._clear_default_addresses(consumer_id)

        addr = DeliveryAddress(
            consumer_id=profile.id,
            label=payload.label,
            recipient_name=payload.recipient_name,
            recipient_phone=payload.recipient_phone,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            landmark=payload.landmark,
            city=payload.city,
            state=payload.state,
            pincode=payload.pincode,
            jurisdiction=payload.jurisdiction,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_default=is_default,
            delivery_instructions=payload.delivery_instructions,
        )
        self.db.add(addr)
        await self.db.commit()
        await self.db.refresh(addr)
        return addr

    async def list_addresses(self, consumer_id: str) -> list[DeliveryAddress]:
        result = await self.db.execute(
            select(DeliveryAddress).where(DeliveryAddress.consumer_id == consumer_id)
            .order_by(DeliveryAddress.is_default.desc(), DeliveryAddress.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_address(self, consumer_id: str, address_id: str) -> None:
        result = await self.db.execute(
            select(DeliveryAddress).where(
                DeliveryAddress.id == address_id,
                DeliveryAddress.consumer_id == consumer_id,
            )
        )
        addr = result.scalar_one_or_none()
        if not addr:
            raise NotFoundError(f"Address {address_id} not found")
        await self.db.delete(addr)
        await self.db.commit()

    # ============================================================
    # AGE VERIFICATION & TIER PROGRESSION
    # ============================================================
    async def submit_age_verification(
        self, consumer_id: str, payload: AgeVerificationSubmit
    ) -> AgeVerificationRecord:
        profile = await self.get_profile(consumer_id)

        today = date.today()
        calculated_age = today.year - payload.date_of_birth.year - (
            (today.month, today.day) < (payload.date_of_birth.month, payload.date_of_birth.day)
        )

        status = "PASSED" if calculated_age >= 21 else "REJECTED"
        doc_hash = hashlib.sha256(payload.document_number.encode()).hexdigest()

        rec = AgeVerificationRecord(
            consumer_id=profile.id,
            verification_type=payload.verification_type,
            document_type=payload.document_type,
            document_hash=doc_hash,
            verified_age=calculated_age,
            verification_status=status,
            verifier_provider=payload.verifier_provider,
            details={"dob": payload.date_of_birth.isoformat()},
        )
        self.db.add(rec)

        if status == "PASSED":
            profile.is_age_verified = True
            profile.age_verified_at = datetime.now(timezone.utc)
            profile.date_of_birth = payload.date_of_birth
            profile.consumer_level = "C2_AGE_VERIFIED"
            profile.trust_score = min(profile.trust_score + 25, 100)

        await self.db.commit()
        await self.db.refresh(rec)

        await self._publish("consumer.age_verified", {
            "consumer_id": profile.id, "status": status, "calculated_age": calculated_age,
        })
        return rec

    # ============================================================
    # HELPERS
    # ============================================================
    async def _clear_default_addresses(self, consumer_id: str) -> None:
        await self.db.execute(
            update(DeliveryAddress)
            .where(DeliveryAddress.consumer_id == consumer_id)
            .values(is_default=False)
        )

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-consumer")
            await self.producer.publish("consumer.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
