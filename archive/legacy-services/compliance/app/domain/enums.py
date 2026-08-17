"""Compliance domain enums."""

from __future__ import annotations

from enum import Enum


class DecisionStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


class RuleType(str, Enum):
    AGE = "age"
    PRODUCT = "product"
    QUANTITY = "quantity"
    TIME = "time"
    LOCATION = "location"
    LICENSE = "license"
    VERIFICATION = "verification"
    DELIVERY = "delivery"


class Operator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"


class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class DecisionReasonCode(str, Enum):
    AGE_REQUIREMENT_FAILED = "age_requirement_failed"
    VERIFICATION_REQUIRED = "verification_required"
    PRODUCT_RESTRICTED = "product_restricted"
    QUANTITY_LIMIT_EXCEEDED = "quantity_limit_exceeded"
    TIME_RESTRICTION = "time_restriction"
    LOCATION_RESTRICTED = "location_restricted"
    NO_POLICY = "no_policy"
    POLICY_EXPIRED = "policy_expired"
