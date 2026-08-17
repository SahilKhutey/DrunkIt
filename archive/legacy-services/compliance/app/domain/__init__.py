"""Compliance domain package."""

from .decision import EligibilityDecision, RuleResult
from .enums import DecisionReasonCode, DecisionStatus, Operator, PolicyStatus, RuleType
from .events import EligibilityEvaluatedEvent
from .exceptions import (
    ComplianceDomainError,
    JurisdictionNotFoundError,
    NoActivePolicyError,
    PolicyEvaluationError,
)

__all__ = [
    "ComplianceDomainError",
    "DecisionReasonCode",
    "DecisionStatus",
    "EligibilityDecision",
    "EligibilityEvaluatedEvent",
    "JurisdictionNotFoundError",
    "NoActivePolicyError",
    "Operator",
    "PolicyEvaluationError",
    "PolicyStatus",
    "RuleResult",
    "RuleType",
]
