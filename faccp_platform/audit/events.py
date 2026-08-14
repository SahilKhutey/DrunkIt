"""AuditEvent constants for security and platform audit logging."""

from __future__ import annotations


class AuditEvent:
    """Canonical audit event constants."""

    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    PERMISSION_DENIED = "auth.permission.denied"

    ORDER_CREATED = "order.created"
    ORDER_CANCELLED = "order.cancelled"

    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_REFUNDED = "payment.refunded"

    VERIFICATION_STARTED = "verification.started"
    VERIFICATION_COMPLETED = "verification.completed"

    COMPLIANCE_APPROVED = "compliance.approved"
    COMPLIANCE_REJECTED = "compliance.rejected"
