"""Seed sample support knowledge documents and tickets."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import KnowledgeDocument, SupportTicket
from faccp_common.database import init_engine, session_scope

SAMPLE_DOCS = [
    {
        "title": "State Permit Verification Process",
        "category": "PERMITS",
        "content": "Consumers purchasing in Karnataka or Maharashtra must present verified state liquor permits or age declaration forms upon doorstep delivery.",
        "is_published": True,
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for d in SAMPLE_DOCS:
            existing = await session.execute(
                select(KnowledgeDocument).where(KnowledgeDocument.title == d["title"])
            )
            if existing.scalar_one_or_none() is None:
                doc = KnowledgeDocument(
                    title=d["title"],
                    category=d["category"],
                    content=d["content"],
                    is_published=d["is_published"],
                )
                session.add(doc)
                print(f"  Knowledge document seeded: {d['title']}")

        tck = SupportTicket(
            ticket_number="TCK-SEED-001",
            subject="Permit Verification Inquiry",
            description="How do I upload my Karnataka L-18 excise permit?",
            status="OPEN",
            priority="NORMAL",
            source="AI_AGENT",
        )
        session.add(tck)

    print("\n[OK] Seeded support agent knowledge base and tickets.")


if __name__ == "__main__":
    asyncio.run(seed())
