from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    default_message: str = "An internal error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    error_code = "BAD_REQUEST"
    default_message = "Invalid request."


class ValidationError(AppError):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    default_message = "Validation failed."


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "UNAUTHORIZED"
    default_message = "Authentication required."


class InvalidCredentialsError(UnauthorizedError):
    error_code = "INVALID_CREDENTIALS"
    default_message = "Invalid credentials."


class TokenExpiredError(UnauthorizedError):
    error_code = "TOKEN_EXPIRED"
    default_message = "Token has expired."


class ForbiddenError(AppError):
    status_code = 403
    error_code = "FORBIDDEN"
    default_message = "You do not have permission to perform this action."


class ABACDeniedError(ForbiddenError):
    error_code = "ABAC_DENIED"
    default_message = "Access denied by attribute policy."


class SeparationOfDutiesError(ForbiddenError):
    error_code = "SOD_VIOLATION"
    default_message = "Action blocked by separation-of-duties policy."


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"
    default_message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    error_code = "CONFLICT"
    default_message = "Resource already exists or state conflict."


class RateLimitError(AppError):
    status_code = 429
    error_code = "RATE_LIMITED"
    default_message = "Too many requests."


class StateTransitionError(ConflictError):
    error_code = "INVALID_STATE_TRANSITION"
    default_message = "Invalid state transition."


class InternalError(AppError):
    status_code = 500
    error_code = "INTERNAL_ERROR"
    default_message = "Internal server error."


class ServiceUnavailableError(AppError):
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
    default_message = "Service temporarily unavailable."


class IntegrationError(AppError):
    status_code = 502
    error_code = "INTEGRATION_ERROR"
    default_message = "Upstream integration failed."


class ComplianceDeniedError(ForbiddenError):
    error_code = "COMPLIANCE_DENIED"
    default_message = "Transaction denied by compliance policy."


class AgeNotVerifiedError(ForbiddenError):
    error_code = "AGE_NOT_VERIFIED"
    default_message = "Age eligibility not verified."


class LicenseInvalidError(ForbiddenError):
    error_code = "LICENSE_INVALID"
    default_message = "Retailer license is not valid."


class VerificationFailedError(ForbiddenError):
    error_code = "VERIFICATION_FAILED"
    default_message = "Identity/age verification failed."
