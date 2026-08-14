"""CLI script to seed RBAC permissions."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from faccp_platform.database.base import Base
from faccp_platform.database.models import Permission
from faccp_platform.database.session import get_session_manager

PERMISSIONS = [
    ("users", "read"),
    ("users", "create"),
    ("users", "update"),
    ("users", "delete"),
    ("orders", "read"),
    ("orders", "create"),
    ("orders", "update"),
    ("orders", "delete"),
    ("inventory", "read"),
    ("inventory", "update"),
    ("audit", "read"),
]


async def seed() -> None:
    session_manager = get_session_manager()
    async with session_manager.session() as session:
        for resource, action in PERMISSIONS:
            result = await session.execute(
                select(Permission).where(
                    Permission.resource == resource, Permission.action == action
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                perm = Permission(resource=resource, action=action)
                session.add(perm)
                print(f"Seeded permission: {resource}:{action}")
        await session.commit()
    print("Permissions seed complete.")


def main() -> int:
    asyncio.run(seed())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
