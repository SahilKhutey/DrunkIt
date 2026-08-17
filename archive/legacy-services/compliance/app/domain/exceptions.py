"""Compliance domain exceptions."""

from __future__ import annotations


class ComplianceDomainError(Exception):
    """Base exception for compliance domain errors."""
    pass


class NoActivePolicyError(ComplianceDomainError):
    """Raised when no active policy is found for a jurisdiction."""
    pass


class JurisdictionNotFoundError(ComplianceDomainError):
    """Raised when specified jurisdiction is not found."""
    pass


class PolicyEvaluationError(ComplianceDomainError):
    """Raised when policy evaluation fails unexpectedly."""
    pass
