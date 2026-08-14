"""Unit tests for RBAC and resource-level authorization (IDOR protection)."""

import pytest
from fastapi import HTTPException
from faccp_platform.security.authorization import authorize_resource_access, can_access_resource
from faccp_platform.security.claims import TokenClaims
from faccp_platform.security.permissions import Permission


def test_resource_access_control():
    """Verify resource-level access control (IDOR prevention)."""
    user_a = TokenClaims(
        sub="user-A",
        iss="auth",
        aud="api",
        exp=2000,
        iat=1000,
        jti="jti1",
        roles=["consumer"],
        permissions=[Permission.ORDER_READ],
    )
    user_b = TokenClaims(
        sub="user-B",
        iss="auth",
        aud="api",
        exp=2000,
        iat=1000,
        jti="jti2",
        roles=["consumer"],
        permissions=[Permission.ORDER_READ],
    )
    admin = TokenClaims(
        sub="admin-1",
        iss="auth",
        aud="api",
        exp=2000,
        iat=1000,
        jti="jti3",
        roles=["admin"],
        permissions=[Permission.ADMIN_READ],
    )

    # User A accesses User A's order -> Allowed
    assert can_access_resource(user_a, "user-A") is True

    # User B accesses User A's order -> Denied (IDOR protection)
    assert can_access_resource(user_b, "user-A") is False

    # Admin accesses User A's order -> Allowed
    assert can_access_resource(admin, "user-A") is True


@pytest.mark.asyncio
async def test_authorize_resource_access_exception():
    """Verify authorize_resource_access raises HTTP 403 on cross-user resource access attempt."""
    user_b = TokenClaims(
        sub="user-B",
        iss="auth",
        aud="api",
        exp=2000,
        iat=1000,
        jti="jti2",
        roles=["consumer"],
        permissions=[Permission.ORDER_READ],
    )
    with pytest.raises(HTTPException) as exc_info:
        await authorize_resource_access(user_b, "user-A")

    assert exc_info.value.status_code == 403
    assert "Forbidden" in exc_info.value.detail
