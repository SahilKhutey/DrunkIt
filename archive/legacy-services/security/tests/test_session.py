import pytest
from services.security.app.services.session_service import SessionService


@pytest.mark.asyncio
async def test_session_creation_and_revocation():
    svc = SessionService()
    sess = await svc.create_session("user-sess-100")
    assert sess["status"] == "ACTIVE"

    rev = await svc.revoke_session(sess["id"])
    assert rev["status"] == "REVOKED"
