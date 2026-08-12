"""
Policy Access Guard as codified in Article 3 of the System Constitution (§3.1).
Ensures no business service hardcodes compliance rules.
"""

from __future__ import annotations

import re


class PolicyAccessGuard:
    """Enforces that no business service hardcodes compliance rules."""

    FORBIDDEN_PATTERNS: list[str] = [
        r"if\s+.*\.age\s*[<>]=\s*\d+",  # Hardcoded age checks
        r"if\s+.*'dry_day'|if\s+.*dry_day",
        r"\bmin_age\s*=\s*21\b",  # Hardcoded age constants
        r"if\s+now\(\)\.hour\s*[<>]=\s*\d+",  # Hardcoded operating hours
    ]

    ALLOWED_SOURCES: set[str] = {
        "compliance-service",
        "policy-service",
        "policies/",
        "_common",
        "tests/",
    }

    @classmethod
    def audit(cls, file_path: str, content: str) -> list[str]:
        """Return list of compliance rule isolation violations found in file."""
        violations = []
        normalized_path = file_path.replace("\\", "/")
        if any(allowed in normalized_path for allowed in cls.ALLOWED_SOURCES):
            return violations

        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, content):
                violations.append(f"Hardcoded compliance rule in {file_path}: matching pattern '{pattern}'")
        return violations
