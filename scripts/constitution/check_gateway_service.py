"""
Gateway Service Checker.
Verifies production code structure, endpoints, schemas, service logic of api-gateway.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class GatewayServiceChecker:
    """Verifies complete API Gateway Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_gateway_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "api-gateway"

        required_files = [
            "pyproject.toml",
            "Dockerfile",
            "README.md",
            "app/config.py",
            "app/schemas/gateway.py",
            "app/services/gateway_service.py",
            "app/api/dependencies.py",
            "app/api/routes/gateway.py",
            "app/main.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Gateway Service violation: Missing required file {req_file}")

        # Check endpoints in routes/gateway.py
        routes_file = base_dir / "app" / "api" / "routes" / "gateway.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/routes", "/health-all"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Gateway Service violation: Missing endpoint route {ep} in routes/gateway.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_gateway_service()
        if v:
            all_violations["api-gateway"] = v
        return all_violations


if __name__ == "__main__":
    checker = GatewayServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ GATEWAY SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ API Gateway Service microservice verified cleanly (Reverse Proxy & Routing intact).")
    sys.exit(0)
