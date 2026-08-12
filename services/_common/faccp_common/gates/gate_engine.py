"""
8-Gate Development Gate Engine (Protocol 60).
Enforces feature readiness from Requirement (Gate 0) to Post-Production Validation (Gate 8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GateStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"


@dataclass
class DevelopmentGate:
    gate_number: int
    name: str
    owner_role: str
    required_artifacts: list[str]
    approvers: list[str]
    status: GateStatus = GateStatus.NOT_STARTED


class GateRegistry:
    GATES: dict[int, DevelopmentGate] = {
        0: DevelopmentGate(0, "Requirement Definition", "Product Manager", ["BRD", "Acceptance Criteria"], ["Product Manager", "Domain Owner"]),
        1: DevelopmentGate(1, "Architecture Design", "Tech Lead", ["Domain Identification", "API Contract", "ADR"], ["Tech Lead", "Security Architect"]),
        2: DevelopmentGate(2, "Trust & Security Design", "Security Architect", ["Authentication Flow", "Authorization Model", "Threat Model"], ["Security Architect", "Compliance Officer"]),
        3: DevelopmentGate(3, "Privacy Impact Assessment", "Data Protection Officer", ["Data Classification", "PII Inventory", "Retention Policy"], ["Data Protection Officer"]),
        4: DevelopmentGate(4, "Compliance Review", "Compliance Officer", ["Applicable Jurisdictions", "Policy Version", "Audit Events"], ["Compliance Officer"]),
        5: DevelopmentGate(5, "Engineering Implementation", "Tech Lead", ["Unit Tests", "Integration Tests", "Documentation"], ["Tech Lead", "Code Owner"]),
        6: DevelopmentGate(6, "Security Validation", "Security Team", ["SAST Scan", "DAST Scan", "Secret Scan"], ["Security Team"]),
        7: DevelopmentGate(7, "Production Readiness", "SRE Lead", ["Monitoring Configured", "Rollback Plan", "Load Test"], ["SRE Lead", "Product Manager"]),
        8: DevelopmentGate(8, "Post-Production Validation", "PM & Tech Lead", ["Metrics Validated", "Zero Critical Bugs"], ["Product Manager", "Tech Lead"]),
    }


class FeatureGateValidator:
    """Validates that a feature has successfully passed all 8 gates."""

    def __init__(self, feature_id: str) -> None:
        self.feature_id = feature_id
        self.gate_statuses: dict[int, GateStatus] = {i: GateStatus.NOT_STARTED for i in range(9)}

    def pass_gate(self, gate_number: int) -> None:
        if gate_number not in GateRegistry.GATES:
            raise ValueError(f"Invalid gate number: {gate_number}")
        # Enforce sequential gate passing
        if gate_number > 0 and self.gate_statuses[gate_number - 1] != GateStatus.PASSED:
            raise RuntimeError(f"Cannot pass Gate {gate_number} before Gate {gate_number - 1} is PASSED!")
        self.gate_statuses[gate_number] = GateStatus.PASSED

    def is_production_ready(self) -> bool:
        """Returns True if Gates 0 through 7 have passed."""
        return all(self.gate_statuses[i] == GateStatus.PASSED for i in range(8))

    def is_feature_complete(self) -> bool:
        """Returns True if all 9 gates (Gate 0 to Gate 8) have passed."""
        return all(self.gate_statuses[i] == GateStatus.PASSED for i in range(9))
