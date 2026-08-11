"""ABAC (Attribute-Based Access Control) engine."""

from faccp_common.abac.engine import (
    ABACEngine, AccessRequest, AccessDecision, PolicyEffect,
    SubjectAttributes, ResourceAttributes, ActionAttributes, EnvironmentAttributes,
)
from faccp_common.abac.policies import build_default_policies

__all__ = [
    "ABACEngine", "AccessRequest", "AccessDecision", "PolicyEffect",
    "SubjectAttributes", "ResourceAttributes", "ActionAttributes", "EnvironmentAttributes",
    "build_default_policies",
]
