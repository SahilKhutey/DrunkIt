from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import pytest

from services.compliance.app.services.verification_service import VerificationService, is_fresh


@pytest.mark.asyncio
async def test_expired_verification():
    verification = MagicMock()
    verification.status = "VERIFIED"
    verification.revoked_at = None
    verification.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

    service = VerificationService()
    result = await service.is_valid(verification)

    assert result is False


def test_verification_freshness():
    now = datetime.now(timezone.utc)
    fresh_time = now - timedelta(seconds=30)
    old_time = now - timedelta(seconds=600)

    assert is_fresh(fresh_time, max_age_seconds=120) is True
    assert is_fresh(old_time, max_age_seconds=120) is False
    assert is_fresh(None, max_age_seconds=120) is False
