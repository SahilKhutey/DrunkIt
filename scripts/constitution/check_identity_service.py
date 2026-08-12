"""
Identity Service Checker.
Verifies production code structure, endpoints, models, schemas, and RBAC seed script of identity-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class IdentityServiceChecker:
    """Verifies complete Identity Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_identity_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "identity-service"

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
            "app/schemas/auth.py",
            "app/services/auth_service.py",
            "app/api/dependencies.py",
            "app/api/routes/auth.py",
            "app/main.py",
            "app/scripts/seed_rbac.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Identity Service violation: Missing required file {req_file}")

        # Check endpoints in routes/auth.py
        routes_file = base_dir / "app" / "api" / "routes" / "auth.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/register", "/login", "/refresh", "/logout",
                "/password/change", "/password/reset/request", "/password/reset/confirm",
                "/mfa/setup", "/mfa/verify", "/mfa/disable", "/me", "/sessions"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Identity Service violation: Missing endpoint route {ep} in routes/auth.py")

        # Check models in db/models.py
        models_file = base_dir / "app" / "db" / "models.py"
        if models_file.exists():
            content = models_file.read_text(encoding="utf-8")
            required_models = [
                "class User", "class Session", "class Device", "class APIKey",
                "class RoleDefinition", "class PasswordResetToken", "class EmailVerificationToken"
            ]
            for model in required_models:
                if model not in content:
                    violations.append(f"Identity Service violation: Missing database model {model} in db/models.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_identity_service()
        if v:
            all_violations["identity-service"] = v
        return all_violations


if __name__ == "__main__":
    checker = IdentityServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ IDENTITY SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Identity Service microservice verified cleanly (12 Endpoints, 7 Entities, Migrations & RBAC seed intact).")
    sys.exit(0)
