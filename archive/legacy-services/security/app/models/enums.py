from enum import Enum


class RiskLevel(str, Enum):

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"


class RiskDecision(str, Enum):

    ALLOW = "ALLOW"

    MONITOR = "MONITOR"

    STEP_UP = "STEP_UP"

    HOLD = "HOLD"

    BLOCK = "BLOCK"

    REVIEW = "REVIEW"


class SecurityAction(str, Enum):

    NONE = "NONE"

    STEP_UP = "STEP_UP"

    TEMPORARY_HOLD = "TEMPORARY_HOLD"

    SESSION_REVOKE = "SESSION_REVOKE"

    ACCOUNT_LOCK = "ACCOUNT_LOCK"

    ORDER_HOLD = "ORDER_HOLD"

    CASE_CREATE = "CASE_CREATE"
