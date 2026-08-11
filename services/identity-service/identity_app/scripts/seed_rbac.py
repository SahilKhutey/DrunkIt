from __future__ import annotations

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from faccp_common.roles import ROLE_PERMISSIONS, Permission, Role
from identity_app.config import get_settings
from identity_app.db.models import PermissionModel, RoleModel


async def seed() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async with AsyncSession(engine) as session:
        print("Seeding RBAC roles and permissions...")

        # 1. Ensure all permissions exist
        perm_objs: dict[str, PermissionModel] = {}
        for p in Permission:
            res = await session.execute(select(PermissionModel).where(PermissionModel.code == p.value))
            existing = res.scalar_one_or_none()
            if not existing:
                existing = PermissionModel(code=p.value, description=f"Permission for {p.value}")
                session.add(existing)
            perm_objs[p.value] = existing

        await session.flush()

        # 2. Ensure all roles exist and link permissions
        for r in Role:
            res = await session.execute(select(RoleModel).where(RoleModel.name == r.value))
            role_obj = res.scalar_one_or_none()
            if not role_obj:
                role_obj = RoleModel(name=r.value, description=f"System role {r.value}")
                session.add(role_obj)

            allowed_perms = ROLE_PERMISSIONS.get(r, set())
            role_obj.permissions = [perm_objs[p.value] for p in allowed_perms if p.value in perm_objs]

        await session.commit()
        print("RBAC roles & permissions seeded successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
