"""Consumer Profile domain service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.profile import ConsumerProfile
from ..repositories.profile import ProfileRepository
from ..schemas.profile import ProfileUpdate


class ProfileService:
    """Business service managing consumer profile details."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfileRepository(session)

    async def get(self, consumer_id: str | uuid.UUID) -> ConsumerProfile | None:
        """Fetch profile for consumer."""
        return await self.repository.get(consumer_id)

    async def update(
        self,
        consumer_id: str | uuid.UUID,
        data: ProfileUpdate,
    ) -> ConsumerProfile:
        """Update consumer profile attributes."""
        return await self.repository.create_or_update(
            consumer_id,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            preferences=data.preferences,
        )
