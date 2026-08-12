"""Seed sample fraud rules and risk evaluations."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import FraudPatternRule
from faccp_common.database import init_engine, session_scope

SAMPLE_RULES = [
    {
        "rule_name": "RULE_HIGH_VELOCITY_1H",
        "description": "More than 3 transactions in 1 hour from single consumer account",
        "risk_score_impact": 0.40,
    },
    {
        "rule_name": "RULE_LARGE_AMOUNT_THRESHOLD",
        "description": "Transaction total exceeding INR 25,000 in single order",
        "risk_score_impact": 0.35,
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for r in SAMPLE_RULES:
            existing = await session.execute(
                select(FraudPatternRule).where(FraudPatternRule.rule_name == r["rule_name"])
            )
            if existing.scalar_one_or_none() is None:
                rule = FraudPatternRule(
                    rule_name=r["rule_name"],
                    description=r["description"],
                    risk_score_impact=r["risk_score_impact"],
                    is_active=True,
                )
                session.add(rule)
                print(f"  Fraud pattern rule seeded: {r['rule_name']} (+{r['risk_score_impact']})")

    print("\n[OK] Seeded fraud pattern rules.")


if __name__ == "__main__":
    asyncio.run(seed())
