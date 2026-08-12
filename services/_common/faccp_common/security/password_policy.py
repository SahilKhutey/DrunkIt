"""
Password Policy standard as codified in Article 1 of the System Constitution (§1.2).
"""

from __future__ import annotations


class PasswordPolicy:
    MIN_LENGTH = 12
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    BREACH_CHECK_ENABLED = True  # Check against HaveIBeenPwned
    ROTATION_DAYS = 0  # No forced rotation (NIST 800-63B compliant)
    HISTORY_COUNT = 5  # Cannot reuse last 5 passwords

    @classmethod
    def validate(cls, password: str, user_email: str | None = None) -> tuple[bool, str]:
        """Validate a proposed password against System Constitution standards."""
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"
        if len(password) > cls.MAX_LENGTH:
            return False, f"Password cannot exceed {cls.MAX_LENGTH} characters"
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain an uppercase letter"
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain a lowercase letter"
        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain a digit"
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            return False, "Password must contain a special character"
        if user_email:
            username = user_email.split("@")[0].lower()
            if len(username) >= 3 and username in password.lower():
                return False, "Password cannot contain email username"
        return True, ""
