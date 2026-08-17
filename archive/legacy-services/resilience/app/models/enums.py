from enum import Enum


class FailureClass(str, Enum):

    TRANSIENT = "TRANSIENT"

    DEPENDENCY = "DEPENDENCY"

    DATA = "DATA"

    NETWORK = "NETWORK"

    INFRASTRUCTURE = "INFRASTRUCTURE"

    SECURITY = "SECURITY"

    COMPLIANCE = "COMPLIANCE"

    UNKNOWN = "UNKNOWN"


class CircuitState(str, Enum):

    CLOSED = "CLOSED"

    OPEN = "OPEN"

    HALF_OPEN = "HALF_OPEN"


class PlatformMode(str, Enum):

    NORMAL = "NORMAL"

    DEGRADED = "DEGRADED"

    EMERGENCY = "EMERGENCY"

    READ_ONLY = "READ_ONLY"

    RECOVERY = "RECOVERY"


class RecoveryState(str, Enum):

    DETECTED = "DETECTED"

    ASSESSING = "ASSESSING"

    ISOLATED = "ISOLATED"

    RESTORING = "RESTORING"

    VERIFYING = "VERIFYING"

    REACTIVATING = "REACTIVATING"

    COMPLETE = "COMPLETE"

    FAILED = "FAILED"
