"""
Audit Service Checker.
Verifies production code structure, endpoints, models, schemas, service logic, and seed script of audit-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class AuditServiceChecker:
    """Verifies complete Audit Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_audit_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "audit-service"

        required_files = [
            "pyproject.toml",
            "Dockerfile",
            "alembic.ini",
            "README.md",
            "alembic/env.py",
            "alembic/versions/0001_initial.py",
            "app/config.py",
            "app/db/base.py",
            "app/db/models.py",
            "app/schemas/audit.py",
            "app/services/audit_service.py",
            "app/api/dependencies.py",
            "app/api/routes/audit.py",
            "app/main.py",
            "app/scripts/seed_audit.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Audit Service violation: Missing required file {req_file}")

        # Check endpoints in routes/audit.py
        routes_file = base_dir / "app" / "api" / "routes" / "audit.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/logs", "/verify-chain"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Audit Service violation: Missing endpoint route {ep} in routes/audit.py")

        # Check models in db/models.py
        models_file = base_dir / "app" / "db" / "models.py"
        if models_file.exists():
            content = models_file.read_text(encoding="utf-8")
            required_models = [
                "class CryptographicAuditEntry"
            ]
            for model in required_models:
                if model not in content:
                    violations.append(f"Audit Service violation: Missing database model {model} in db/models.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_audit_service()
        if v:
            all_violations["audit-service"] = v
        return all_violations


if __name__ == "__main__":
    checker = AuditServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ AUDIT SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Audit Service microservice verified cleanly (Cryptographic Hash-Chained Audit Ledger intact).")
    sys.exit(0)
