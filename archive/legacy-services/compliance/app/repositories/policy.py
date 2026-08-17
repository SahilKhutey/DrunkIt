"""Compliance Policy repository."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.enums import PolicyStatus
from ..models.policy import CompliancePolicy


class PolicyRepository:
    """Repository handling policy persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, policy_id: str | uuid.UUID) -> CompliancePolicy | None:
        """Fetch policy by ID."""
        pid_str = str(policy_id)
        result = await self.session.execute(
            select(CompliancePolicy).where(CompliancePolicy.id == pid_str)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        jurisdiction_id: str | uuid.UUID,
        name: str,
        version: str = "1.0.0",
        effective_from: datetime | None = None,
        effective_until: datetime | None = None,
        status: PolicyStatus = PolicyStatus.DRAFT,
    ) -> CompliancePolicy:
        """Create new compliance policy."""
        jid_str = str(jurisdiction_id)
        eff_from = effective_from or datetime.now(timezone.utc)
        policy = CompliancePolicy(
            jurisdiction_id=jid_str,
            name=name,
            version=version,
            effective_from=eff_from,
            effective_until=effective_until,
            status=status,
        )
        self.session.add(policy)
        await self.session.flush()
        return policy
