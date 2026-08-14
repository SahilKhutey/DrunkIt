"""Contract test for Database Ownership Manifest validation."""

import os
import pytest
import yaml


def test_database_ownership_manifest():
    """Verify database-ownership.yaml manifest maps service table ownership correctly."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    manifest_path = os.path.join(root_dir, "contracts", "database-ownership.yaml")
    assert os.path.exists(manifest_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    assert "order-service" in services
    assert "orders" in services["order-service"]["owns"]
    assert "payment-service" in services
    assert "payments" in services["payment-service"]["owns"]
