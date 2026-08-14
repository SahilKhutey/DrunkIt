"""Security constants for token types, user statuses, and audit actions."""

from __future__ import annotations


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


class UserStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"


class AuditAction:
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"

    USER_CREATED = "identity.user.created"
    USER_DISABLED = "identity.user.disabled"

    ROLE_ASSIGNED = "identity.role.assigned"
    ROLE_REMOVED = "identity.role.removed"

    ACCESS_DENIED = "security.access.denied"
