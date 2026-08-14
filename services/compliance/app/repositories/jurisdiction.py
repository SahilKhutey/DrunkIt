"""Jurisdiction repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.jurisdiction import Jurisdiction


class JurisdictionRepository:
    """Repository handling jurisdiction persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, jurisdiction_id: str | uuid.UUID) -> Jurisdiction | None:
        """Fetch jurisdiction by ID."""
        jid_str = str(jurisdiction_id)
        result = await self.session.execute(
            select(Jurisdiction).where(Jurisdiction.id == jid_str)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, country_code: str, state_code: str | None = None) -> Jurisdiction | None:
        """Fetch jurisdiction by country and state code."""
        stmt = select(Jurisdiction).where(Jurisdiction.country_code == country_code)
        if state_code:
            stmt = stmt.where(Jurisdiction.state_code == state_code)
        else:
            stmt = stmt.where(Jurisdiction.state_code.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, country_code: str, state_code: str | None = None) -> Jurisdiction:
        """Create new jurisdiction record."""
        jurisdiction = Jurisdiction(country_code=country_code, state_code=state_code)
        self.session.add(jurisdiction)
        await self.session.flush()
        return jurisdiction
