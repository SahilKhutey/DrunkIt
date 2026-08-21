"""Domain and HTTP exception hierarchy for DrunkIt v0.1."""

from typing import Any


class DrunkItError(Exception):
    """Base exception for all DrunkIt platform errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundError(DrunkItError):
    """Raised when an identified resource cannot be found."""

    def __init__(
        self,
        message: str = "Requested resource was not found.",
        code: str = "RESOURCE_NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=404, details=details)


class ValidationError(DrunkItError):
    """Raised when client input fails business or schema validation."""

    def __init__(
        self,
        message: str = "Input validation failed.",
        code: str = "VALIDATION_FAILED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=422, details=details)


class UnauthorizedError(DrunkItError):
    """Raised when an unauthenticated request attempts to access a protected resource."""

    def __init__(
        self,
        message: str = "Authentication is required to access this resource.",
        code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=401, details=details)


class ForbiddenError(DrunkItError):
    """Raised when an authenticated principal lacks required RBAC privileges."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=403, details=details)


class ConflictError(DrunkItError):
    """Raised when a unique constraint or concurrency conflict occurs."""

    def __init__(
        self,
        message: str = "Resource conflict detected.",
        code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=409, details=details)


class ComplianceDeniedError(DrunkItError):
    """Raised when a statutory compliance evaluation rejects a requested operation."""

    def __init__(
        self,
        message: str = "Operation denied by jurisdiction statutory compliance policies.",
        code: str = "COMPLIANCE_DENIED",
        reason_codes: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        merged_details = details or {}
        if reason_codes:
            merged_details["reason_codes"] = reason_codes
        super().__init__(message=message, code=code, status_code=403, details=merged_details)


class RateLimitExceededError(DrunkItError):
    """Raised when a client exceeds permitted request frequency."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please retry later.",
        code: str = "RATE_LIMIT_EXCEEDED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=429, details=details)
