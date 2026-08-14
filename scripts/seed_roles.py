"""CLI script to seed RBAC default roles."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from faccp_platform.database.models import Permission, Role
from faccp_platform.database.session import get_session_manager

ROLES = {
    "consumer": "Standard platform consumer",
    "operator": "Platform operational user",
    "admin": "Platform administrator",
}


async def seed() -> None:
    session_manager = get_session_manager()
    async with session_manager.session() as session:
        # Fetch all permissions
        perm_res = await session.execute(select(Permission))
        all_perms = perm_res.scalars().all()

        for name, description in ROLES.items():
            result = await session.execute(select(Role).where(Role.name == name))
            existing = result.scalar_one_or_none()
            if not existing:
                role = Role(name=name, description=description)
                if name == "admin":
                    role.permissions = list(all_perms)
                session.add(role)
                print(f"Seeded role: {name}")
        await session.commit()
    print("Roles seed complete.")


def main() -> int:
    asyncio.run(seed())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
