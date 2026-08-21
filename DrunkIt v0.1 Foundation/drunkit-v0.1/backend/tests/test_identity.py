"""Comprehensive test suite for Identity, Authentication, and RBAC authorization."""

import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.main import app
from app.models.audit import AuditLog, OutboxEvent
from app.models.identity import User

# Test-only admin-guarded router to test RBAC dependency
rbac_guard_router = APIRouter(prefix="/api/v1/test-rbac", tags=["test"])


@rbac_guard_router.get("/admin-only")
def admin_only_endpoint(current_user: User = Depends(require_roles("ADMIN"))) -> dict[str, str]:
    return {"message": f"Welcome Admin {current_user.id}"}


@rbac_guard_router.get("/retailer-only")
def retailer_only_endpoint(current_user: User = Depends(require_roles("RETAILER"))) -> dict[str, str]:
    return {"message": f"Welcome Retailer {current_user.id}"}


# Register test router on app
app.include_router(rbac_guard_router)


def test_register_consumer_success(client: TestClient, db_session: Session) -> None:
    """Verify consumer registration creates user, roles, consumer profile, and audit/outbox entries."""
    payload = {
        "email": "consumer.kolkata@example.com",
        "phone": "+919830012345",
        "password": "SecurePassword123!",
        "role": "CONSUMER",
        "preferred_market": "IN-WB",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "consumer.kolkata@example.com"
    assert data["phone"] == "+919830012345"
    assert "CONSUMER" in data["roles"]
    assert data["consumer_profile"]["preferred_market"] == "IN-WB"
    assert data["consumer_profile"]["date_of_birth_verified"] is False

    # Check Outbox and Audit entries
    audit = db_session.scalars(
        select(AuditLog).where(AuditLog.action == "USER_REGISTERED")
    ).first()
    assert audit is not None
    assert audit.metadata_json["role"] == "CONSUMER"

    outbox = db_session.scalars(
        select(OutboxEvent).where(OutboxEvent.event_type == "USER_REGISTERED")
    ).first()
    assert outbox is not None
    assert outbox.payload["email"] == "consumer.kolkata@example.com"


def test_register_duplicate_email_conflict(client: TestClient) -> None:
    """Verify duplicate email registration returns 409 Conflict with standard error envelope."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "role": "CONSUMER",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert data["error"]["code"] == "CONFLICT"
    assert "request_id" in data["error"]


def test_register_retailer_and_brand_roles(client: TestClient) -> None:
    """Verify registration with RETAILER and BRAND roles."""
    res_ret = client.post(
        "/api/v1/auth/register",
        json={
            "email": "retailer@kolkataspirit.com",
            "password": "RetailerPassword123!",
            "role": "RETAILER",
        },
    )
    assert res_ret.status_code == 201
    assert "RETAILER" in res_ret.json()["roles"]

    res_brand = client.post(
        "/api/v1/auth/register",
        json={
            "email": "brand@indrisinglemalt.com",
            "password": "BrandPassword123!",
            "role": "BRAND",
        },
    )
    assert res_brand.status_code == 201
    assert "BRAND" in res_brand.json()["roles"]


def test_login_success_and_token_response(client: TestClient) -> None:
    """Verify login returns valid JWT bearer token and user summary."""
    # 1. Register user
    reg_payload = {
        "email": "login.test@drunkit.in",
        "password": "LoginSecret2026!",
        "role": "CONSUMER",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Authenticate
    login_payload = {
        "email": "login.test@drunkit.in",
        "password": "LoginSecret2026!",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert data["user"]["email"] == "login.test@drunkit.in"
    assert "CONSUMER" in data["user"]["roles"]


def test_login_invalid_password_unauthorized(client: TestClient) -> None:
    """Verify login with incorrect password returns 401 Unauthorized."""
    # 1. Register
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpwd@drunkit.in", "password": "CorrectPassword123!"},
    )

    # 2. Login with bad password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpwd@drunkit.in", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_get_me_authenticated_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/auth/me returns principal information when supplied with Bearer token."""
    # 1. Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"email": "me.test@drunkit.in", "password": "Password123!"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "me.test@drunkit.in", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    # 2. Call /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["email"] == "me.test@drunkit.in"
    assert "CONSUMER" in data["roles"]


def test_get_me_unauthenticated_fails(client: TestClient) -> None:
    """Verify GET /api/v1/auth/me without authorization header returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_rbac_guard_admin_and_retailer(client: TestClient) -> None:
    """Verify RBAC role guards: ADMIN allowed on admin endpoints, CONSUMER denied with 403."""
    # 1. Register Consumer
    client.post(
        "/api/v1/auth/register",
        json={"email": "regular.user@example.com", "password": "Password123!", "role": "CONSUMER"},
    )
    consumer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "regular.user@example.com", "password": "Password123!"},
    ).json()["access_token"]

    # 2. Register Admin
    client.post(
        "/api/v1/auth/register",
        json={"email": "admin.user@example.com", "password": "Password123!", "role": "ADMIN"},
    )
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.user@example.com", "password": "Password123!"},
    ).json()["access_token"]

    # 3. Register Retailer
    client.post(
        "/api/v1/auth/register",
        json={"email": "retailer.user@example.com", "password": "Password123!", "role": "RETAILER"},
    )
    retailer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "retailer.user@example.com", "password": "Password123!"},
    ).json()["access_token"]

    # Test Consumer accessing admin endpoint -> 403 Forbidden
    res_consumer_on_admin = client.get(
        "/api/v1/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {consumer_token}"},
    )
    assert res_consumer_on_admin.status_code == 403
    assert res_consumer_on_admin.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

    # Test Admin accessing admin endpoint -> 200 OK
    res_admin_on_admin = client.get(
        "/api/v1/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin_on_admin.status_code == 200
    assert "Welcome Admin" in res_admin_on_admin.json()["message"]

    # Test Retailer accessing retailer endpoint -> 200 OK
    res_retailer_on_retailer = client.get(
        "/api/v1/test-rbac/retailer-only",
        headers={"Authorization": f"Bearer {retailer_token}"},
    )
    assert res_retailer_on_retailer.status_code == 200
    assert "Welcome Retailer" in res_retailer_on_retailer.json()["message"]

    # Test Consumer accessing retailer endpoint -> 403 Forbidden
    res_consumer_on_retailer = client.get(
        "/api/v1/test-rbac/retailer-only",
        headers={"Authorization": f"Bearer {consumer_token}"},
    )
    assert res_consumer_on_retailer.status_code == 403


def test_logout_endpoint(client: TestClient) -> None:
    """Verify POST /api/v1/auth/logout terminates session."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "logout.test@example.com", "password": "Password123!"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "logout.test@example.com", "password": "Password123!"},
    ).json()["access_token"]

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
