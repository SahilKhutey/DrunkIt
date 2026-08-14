"""Integration tests for Identity Registration, Login, JWT tokens, and Authorization guards."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.database.base import Base
from faccp_platform.identity.schemas import LoginRequest, RegisterRequest
from faccp_platform.identity.service import IdentityService
from faccp_platform.security.dependencies import get_current_principal
from faccp_platform.security.permissions import require_permission
from faccp_platform.security.principal import Principal
from faccp_platform.security.tokens import TokenService
from faccp_platform.audit.service import AuditService


@pytest.mark.asyncio
async def test_identity_service_registration_and_authentication():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        service = IdentityService(session)
        audit_service = AuditService(session)

        # Register user
        user = await service.register(
            email="developer@example.com",
            password="StrongPassword!123",
            first_name="Dev",
            last_name="User",
        )
        assert user.id is not None
        assert user.email == "developer@example.com"
        assert user.password_hash != "StrongPassword!123"

        # Duplicate registration raises error
        with pytest.raises(ValueError, match="Email already registered"):
            await service.register(
                email="DEVELOPER@example.com",
                password="StrongPassword!123",
            )

        # Authentication success
        authenticated = await service.authenticate(
            email="developer@example.com",
            password="StrongPassword!123",
        )
        assert authenticated is not None
        assert authenticated.id == user.id

        # Record audit log for successful login
        audit_entry = await audit_service.record(
            action="auth.login.success",
            actor_id=user.id,
            resource_type="user",
            resource_id=str(user.id),
        )
        assert audit_entry.action == "auth.login.success"

        # Authentication failure
        wrong_auth = await service.authenticate(
            email="developer@example.com",
            password="WrongPassword!123",
        )
        assert wrong_auth is None

    await engine.dispose()


def test_protected_endpoint_permissions():
    app = FastAPI()

    @app.get("/orders")
    async def list_orders(principal: Principal = Depends(require_permission("orders:read"))):
        return {"status": "ok", "user": str(principal.user_id)}

    client = TestClient(app)

    # Missing authorization header -> 401
    res_unauth = client.get("/orders")
    assert res_unauth.status_code == 401

    token_service = TokenService()
    user_id = uuid.uuid4()

    # User with insufficient permissions -> 403
    forbidden_token = token_service.create_access_token(
        user_id=user_id,
        permissions=["inventory:read"],
    )
    res_forbidden = client.get(
        "/orders", headers={"Authorization": f"Bearer {forbidden_token}"}
    )
    assert res_forbidden.status_code == 403

    # User with required permission -> 200
    valid_token = token_service.create_access_token(
        user_id=user_id,
        permissions=["orders:read"],
    )
    res_allowed = client.get(
        "/orders", headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert res_allowed.status_code == 200
    assert res_allowed.json()["user"] == str(user_id)
