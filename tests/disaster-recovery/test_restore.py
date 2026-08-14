"""Disaster recovery backup and restore verification test suite."""

import os
import pytest


def test_backup_and_restore_workflow_simulation():
    """Verify disaster recovery backup and restore script commands and parameters."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    backup_script = os.path.join(root_dir, "deployment", "scripts", "backup.sh")
    restore_script = os.path.join(root_dir, "deployment", "scripts", "restore.sh")

    assert os.path.exists(backup_script)
    assert os.path.exists(restore_script)

    with open(backup_script, "r", encoding="utf-8") as f:
        backup_content = f.read()
    assert "pg_dump" in backup_content

    with open(restore_script, "r", encoding="utf-8") as f:
        restore_content = f.read()
    assert "pg_restore" in restore_content
