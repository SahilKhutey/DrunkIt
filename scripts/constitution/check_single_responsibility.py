"""
Single Responsibility Checker & God Service Detector (§10.1 & §10.8).
Ensures one-sentence responsibility statements and flags overloaded God Services.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path


class SingleResponsibilityChecker:
    """Detects services violating Single Responsibility Protocol."""

    FORBIDDEN_CONNECTORS = [" and ", " plus "]
    MAX_PUBLIC_METHODS = 20
    SUSPICIOUS_METHOD_PATTERNS = [
        r"def\s+.*payment",
        r"def\s+.*order",
        r"def\s+.*inventory",
        r"def\s+.*delivery",
        r"def\s+.*notification",
        r"def\s+.*refund",
        r"def\s+.*verify",
        r"def\s+.*audit",
    ]

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_responsibility_statement(self, responsibility_file: Path) -> list[str]:
        violations = []
        try:
            content = responsibility_file.read_text(encoding="utf-8").strip()
        except Exception:
            return violations

        rel_path = responsibility_file.relative_to(self.root_dir)

        # Check sentence count
        sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 5]
        if len(sentences) > 1:
            violations.append(
                f"{rel_path}: Responsibility spans {len(sentences)} sentences — must fit in ONE sentence (§10.1)"
            )

        # Check connectors
        for conn in self.FORBIDDEN_CONNECTORS:
            if conn in content.lower():
                violations.append(
                    f"{rel_path}: Responsibility statement contains connector '{conn.strip()}' (§10.1)"
                )

        return violations

    def check_class_size(self, py_file: Path) -> list[str]:
        violations = []
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            return violations

        rel_path = py_file.relative_to(self.root_dir)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                public_methods = [
                    m for m in node.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not m.name.startswith("_")
                ]
                if len(public_methods) > self.MAX_PUBLIC_METHODS:
                    violations.append(
                        f"{rel_path}:{node.name} has {len(public_methods)} public methods (max {self.MAX_PUBLIC_METHODS}) (§10.2)"
                    )
        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        services_dir = self.root_dir / "services"
        if not services_dir.exists():
            return all_violations

        # Check RESPONSIBILITY.md files where present
        for resp_file in services_dir.rglob("RESPONSIBILITY.md"):
            v = self.check_responsibility_statement(resp_file)
            if v:
                service = resp_file.parent.name
                all_violations.setdefault(service, []).extend(v)

        # Check class method count ceilings
        for py_file in services_dir.rglob("*.py"):
            if "tests" in py_file.parts or "_common" in py_file.parts:
                continue
            v = self.check_class_size(py_file)
            if v:
                service = py_file.relative_to(services_dir).parts[0]
                all_violations.setdefault(service, []).extend(v)

        return all_violations


if __name__ == "__main__":
    checker = SingleResponsibilityChecker()
    report = checker.check_all()
    if report:
        print("❌ SINGLE RESPONSIBILITY VIOLATIONS DETECTED:")
        for service, viols in report.items():
            print(f"Service: {service}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Single Responsibility Protocol verified cleanly.")
    sys.exit(0)
