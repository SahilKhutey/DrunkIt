"""Unit tests for infrastructure deployment and maintenance shell scripts."""

import os
import pytest


def test_infrastructure_scripts_exist():
    """Verify all infrastructure shell scripts exist and start with bash shebang."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    scripts_dir = os.path.join(root_dir, "infra", "scripts")

    expected_scripts = ["deploy.sh", "rollback.sh", "healthcheck.sh", "backup.sh"]
    for s in expected_scripts:
        path = os.path.join(scripts_dir, s)
        assert os.path.exists(path), f"Script missing: {s}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content.startswith("#!/usr/bin/env bash"), f"Script {s} must start with bash shebang"
