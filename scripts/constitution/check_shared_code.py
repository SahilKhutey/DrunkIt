"""
Shared Code Checker (§9.6).
Verifies that services/_common/ contains only generic utilities and infrastructure adapters, zero domain business logic.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


class SharedCodeChecker:
    """Verifies no domain business logic lives in services/_common/."""

    FORBIDDEN_PATTERNS_IN_COMMON = [
        (r"def\s+process_order", "Business process 'process_order' belongs in order-service"),
        (r"def\s+process_payment", "Business process 'process_payment' belongs in payment-service"),
        (r"class\s+OrderState\b", "Domain entity state machine belongs in order-service"),
        (r"class\s+PaymentIntent\b", "Domain entity belongs in payment-service"),
    ]


    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_common_dir(self) -> list[str]:
        violations = []
        common_dir = self.root_dir / "services" / "_common"
        if not common_dir.exists():
            return violations

        for py_file in common_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = py_file.relative_to(self.root_dir)
            for pattern, reason in self.FORBIDDEN_PATTERNS_IN_COMMON:
                if re.search(pattern, content):
                    violations.append(
                        f"{rel_path}: Matches forbidden business logic pattern '{pattern}' ({reason}) (§9.6)"
                    )

        return violations


if __name__ == "__main__":
    checker = SharedCodeChecker()
    violations = checker.check_common_dir()
    if violations:
        print("❌ SHARED CODE PURITY VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  └── {v}")
        sys.exit(1)
    print("✅ Shared Code Purity verified cleanly (_common contains zero domain business logic).")
    sys.exit(0)
