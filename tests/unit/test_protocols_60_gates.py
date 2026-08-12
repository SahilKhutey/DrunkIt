"""
Unit tests for Protocol 60 & 8-Gate Development Gate System.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.gates import GateRegistry, FeatureGateValidator, GateStatus
from scripts.constitution.check_development_gates import DevelopmentGatesChecker


def test_gate_registry_integrity():
    assert len(GateRegistry.GATES) == 9
    assert GateRegistry.GATES[0].name == "Requirement Definition"
    assert GateRegistry.GATES[7].name == "Production Readiness"
    assert GateRegistry.GATES[8].name == "Post-Production Validation"


def test_feature_gate_validator_flow():
    validator = FeatureGateValidator(feature_id="FEAT-1001")
    assert validator.is_production_ready() is False
    assert validator.is_feature_complete() is False

    # Out of order gate pass raises RuntimeError
    with pytest.raises(RuntimeError):
        validator.pass_gate(2)

    # Sequential passing
    for i in range(8):
        validator.pass_gate(i)
    assert validator.is_production_ready() is True
    assert validator.is_feature_complete() is False

    validator.pass_gate(8)
    assert validator.is_feature_complete() is True


def test_development_gates_checker():
    checker = DevelopmentGatesChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
