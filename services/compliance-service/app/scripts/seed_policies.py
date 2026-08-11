"""Seed default jurisdictions and baseline policies."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

from faccp_common.database import init_engine, session_scope

from app.config import get_settings
from app.services.policy_service import PolicyService


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)

    async with session_scope() as session:
        service = PolicyService(db=session)

        # Default country
        india = await service.create_jurisdiction(
            code="IN", name="India", level="country", country_code="IN",
        )

        states = [
            ("IN-CG", "Chhattisgarh", "Chhattisgarh"),
            ("IN-MH", "Maharashtra", "Maharashtra"),
            ("IN-KA", "Karnataka", "Karnataka"),
            ("IN-DL", "Delhi", "Delhi"),
            ("IN-TN", "Tamil Nadu", "Tamil Nadu"),
            ("IN-GA", "Goa", "Goa"),
        ]
        state_jurisdictions = []
        for code, name, _ in states:
            j = await service.create_jurisdiction(
                code=code, name=name, level="state",
                country_code="IN", parent_code="IN",
            )
            state_jurisdictions.append((code, j))

        for code, _ in state_jurisdictions:
            await service.create_policy(
                jurisdiction_code=code, policy_type="age",
                version="1.0", name=f"Minimum age — {code}",
                rules={"min_age": 21, "verification_required": True},
                effective_from=date.today(),
                effective_until=None,
                approved_by="system_seed",
            )
            await service.create_policy(
                jurisdiction_code=code, policy_type="hours",
                version="1.0", name=f"Sales hours — {code}",
                rules={
                    "start": "10:00", "end": "22:00",
                    "days": [0, 1, 2, 3, 4, 5, 6],
                },
                effective_from=date.today(),
                effective_until=None,
                approved_by="system_seed",
            )
            await service.create_policy(
                jurisdiction_code=code, policy_type="product",
                version="1.0", name=f"Product authorization — {code}",
                rules={
                    "allowed_categories": ["beer", "wine", "spirit", "rtd"],
                    "quantity_limit_per_order": 12,
                },
                effective_from=date.today(),
                effective_until=None,
                approved_by="system_seed",
            )
            await service.create_policy(
                jurisdiction_code=code, policy_type="delivery",
                version="1.0", name=f"Delivery zones — {code}",
                rules={
                    "permitted_zones": ["zone_a", "zone_b", "zone_c"],
                    "delivery_hours": {"start": "10:00", "end": "21:00"},
                },
                effective_from=date.today(),
                effective_until=None,
                approved_by="system_seed",
            )

        await service.add_dry_day(
            jurisdiction_code="IN-CG", day=date.today() + timedelta(days=15),
            reason="Republic Day", approved_by="system_seed",
        )

    print(f"[OK] Seeded {len(states)} states with baseline policies.")


if __name__ == "__main__":
    asyncio.run(seed())
