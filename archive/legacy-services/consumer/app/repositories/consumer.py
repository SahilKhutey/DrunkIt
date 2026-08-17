"""Async Repository for Consumer entities."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.consumer import Consumer


class ConsumerRepository:
    """Repository handling consumer persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, consumer_id: str | uuid.UUID) -> Consumer | None:
        """Fetch consumer by ID."""
        cid_str = str(consumer_id)
        result = await self.session.execute(
            select(Consumer).where(Consumer.id == cid_str)
        )
        return result.scalar_one_or_none()

    async def get_by_identity(self, identity_id: str | uuid.UUID) -> Consumer | None:
        """Fetch consumer by associated identity_id."""
        iid_str = str(identity_id)
        result = await self.session.execute(
            select(Consumer).where(Consumer.identity_id == iid_str)
        )
        return result.scalar_one_or_none()

    async def create(self, identity_id: str | uuid.UUID) -> Consumer:
        """Persist a new Consumer record."""
        iid_str = str(identity_id)
        consumer = Consumer(identity_id=iid_str)
        self.session.add(consumer)
        await self.session.flush()
        return consumer
