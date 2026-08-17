import pytest
from services.payment.app.gateways.mock import MockGateway


def test_webhook_signature_verification():
    gateway = MockGateway()
    assert gateway.verify_webhook(b"{}", "valid_sig") is True

    with pytest.raises(ValueError, match="INVALID_SIGNATURE"):
        gateway.verify_webhook(b"{}", "invalid_sig")
