from __future__ import annotations

import base64
from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.exceptions import ConflictError, NotFoundError
from faccp_common.security import FieldEncryption, create_access_token, pseudonymize
from app.config import get_settings
from app.db.models import ConsumerProfile
from app.schemas.consumer import ProfileCreateRequest, ProfileResponse, ZKAgeClaimResponse

STATE_MIN_AGES = {
    "IN-KA": 21,
    "IN-MH": 25,
    "IN-DL": 21,
    "IN-CG": 21,
    "IN-TN": 21,
    "IN-GA": 18,
}


class ConsumerService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()
        self.enc = FieldEncryption(self.settings.field_encryption_key)

    async def create_profile(self, req: ProfileCreateRequest) -> ProfileResponse:
        existing = await self.db.execute(
            select(ConsumerProfile).where(ConsumerProfile.account_id == req.account_id)
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Profile already exists for this account.")

        today = date.today()
        age = today.year - req.date_of_birth.year - (
            (today.month, today.day) < (req.date_of_birth.month, req.date_of_birth.day)
        )
        min_age = STATE_MIN_AGES.get(req.state_code, 21)
        eligible = age >= min_age
        level = "C3_AGE_ELIGIBLE" if eligible else "C2_IDENTITY_VERIFIED"

        profile = ConsumerProfile(
            account_id=req.account_id,
            full_name_encrypted=self.enc.encrypt(req.full_name),
            date_of_birth_encrypted=self.enc.encrypt(req.date_of_birth.isoformat()),
            date_of_birth_hash=pseudonymize(req.date_of_birth.isoformat()),
            verification_level=level,
            age_eligible=eligible,
            state_code=req.state_code,
            default_delivery_address=req.delivery_address,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        return ProfileResponse(
            id=profile.id,
            account_id=profile.account_id,
            full_name=req.full_name,
            date_of_birth=req.date_of_birth,
            verification_level=profile.verification_level,
            age_eligible=profile.age_eligible,
            state_code=profile.state_code,
            default_delivery_address=profile.default_delivery_address,
            created_at=profile.created_at,
        )

    async def generate_zk_claim(self, consumer_id: str, target_state: str) -> ZKAgeClaimResponse:
        res = await self.db.execute(
            select(ConsumerProfile).where(ConsumerProfile.id == consumer_id)
        )
        profile = res.scalar_one_or_none()
        if not profile:
            raise NotFoundError("Consumer profile not found.")

        dob_str = self.enc.decrypt(profile.date_of_birth_encrypted)
        dob = date.fromisoformat(dob_str)
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        min_age = STATE_MIN_AGES.get(target_state, 21)
        eligible = age >= min_age

        proof = create_access_token(
            subject=profile.id,
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            issuer="faccp-identity-vault",
            audience="faccp-compliance",
            expires_minutes=60,
            claims={
                "claim": "age_eligibility",
                "target_state": target_state,
                "age_eligible": eligible,
                "verification_level": profile.verification_level,
            },
        )

        return ZKAgeClaimResponse(
            consumer_id=profile.id,
            target_state=target_state,
            age_eligible=eligible,
            verification_level=profile.verification_level,
            proof_token=proof,
        )
