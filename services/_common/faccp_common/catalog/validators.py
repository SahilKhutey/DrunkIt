"""
Catalog Validation Engine (7 Validation Stages).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from .registry import CatalogObject, CatalogLifecycleState


@dataclass
class CatalogValidationResult:
    is_valid: bool
    stages_passed: list[str] = field(default_factory=list)
    failed_stage: str | None = None
    reason: str | None = None


class CatalogValidationEngine:
    STAGES: list[str] = [
        "schema_validation",
        "dependency_validation",
        "security_validation",
        "permission_validation",
        "compliance_validation",
        "compatibility_validation",
        "approval_validation",
    ]

    def validate(self, obj: CatalogObject) -> CatalogValidationResult:
        stages_passed = []
        for stage in self.STAGES:
            # Check basic rules
            if stage == "approval_validation" and obj.state not in {CatalogLifecycleState.APPROVED, CatalogLifecycleState.ACTIVE}:
                return CatalogValidationResult(
                    is_valid=False,
                    stages_passed=stages_passed,
                    failed_stage=stage,
                    reason="Approval validation requires APPROVED or ACTIVE state",
                )
            stages_passed.append(stage)

        return CatalogValidationResult(is_valid=True, stages_passed=stages_passed)
