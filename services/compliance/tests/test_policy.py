import pytest
from services.compliance.app.policies.registry import PolicyRegistry


def test_unknown_jurisdiction():
    registry = PolicyRegistry()

    with pytest.raises(ValueError, match="No policy configured for UNKNOWN_JURISDICTION"):
        registry.get("UNKNOWN_JURISDICTION")
