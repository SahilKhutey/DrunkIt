"""
Product Creation Wizard Engine (10 Wizard Steps).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Any, ClassVar


class WizardStep(IntEnum):
    IDENTITY = 1
    CLASSIFICATION = 2
    ATTRIBUTES = 3
    MEDIA = 4
    COMPLIANCE = 5
    VARIANTS = 6
    PREVIEW = 7
    VALIDATION = 8
    REVIEW = 9
    PUBLISH = 10


@dataclass
class ProductCreationContext:
    product_id: str | None = None
    step: WizardStep = WizardStep.IDENTITY
    identity_data: dict[str, Any] = field(default_factory=dict)
    classification_data: dict[str, Any] = field(default_factory=dict)
    attribute_data: dict[str, Any] = field(default_factory=dict)
    media_data: list[dict[str, Any]] = field(default_factory=list)
    compliance_data: dict[str, Any] = field(default_factory=dict)
    variants_data: list[dict[str, Any]] = field(default_factory=list)
    is_validated: bool = False


class ProductWizardEngine:
    STEPS_ORDER: ClassVar[list[WizardStep]] = [
        WizardStep.IDENTITY,
        WizardStep.CLASSIFICATION,
        WizardStep.ATTRIBUTES,
        WizardStep.MEDIA,
        WizardStep.COMPLIANCE,
        WizardStep.VARIANTS,
        WizardStep.PREVIEW,
        WizardStep.VALIDATION,
        WizardStep.REVIEW,
        WizardStep.PUBLISH,
    ]

    def advance_step(self, ctx: ProductCreationContext) -> WizardStep:
        current_idx = self.STEPS_ORDER.index(ctx.step)
        if current_idx < len(self.STEPS_ORDER) - 1:
            ctx.step = self.STEPS_ORDER[current_idx + 1]
        return ctx.step
