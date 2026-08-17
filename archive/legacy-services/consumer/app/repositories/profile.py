"""Async Repository for Consumer Profile entities."""

from __future__ import annotations

import json
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.profile import ConsumerProfile


class ProfileRepository:
    """Repository handling consumer profile operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, consumer_id: str | uuid.UUID) -> ConsumerProfile | None:
        """Fetch profile by consumer_id."""
        cid_str = str(consumer_id)
        result = await self.session.execute(
            select(ConsumerProfile).where(ConsumerProfile.consumer_id == cid_str)
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        consumer_id: str | uuid.UUID,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: date | None = None,
        preferences: dict | None = None,
    ) -> ConsumerProfile:
        """Create or update consumer profile details."""
        cid_str = str(consumer_id)
        profile = await self.get(cid_str)
        pref_str = json.dumps(preferences) if preferences is not None else None

        if profile is None:
            profile = ConsumerProfile(
                consumer_id=cid_str,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                preferences_json=pref_str,
            )
            self.session.add(profile)
        else:
            if first_name is not None:
                profile.first_name = first_name
            if last_name is not None:
                profile.last_name = last_name
            if date_of_birth is not None:
                profile.date_of_birth = date_of_birth
            if pref_str is not None:
                profile.preferences_json = pref_str

        await self.session.flush()
        return profile
