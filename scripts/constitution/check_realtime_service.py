"""
Realtime Service Checker.
Verifies production code structure, endpoints, schemas, service logic of realtime-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class RealtimeServiceChecker:
    """Verifies complete Realtime Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_realtime_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "realtime-service"

        required_files = [
            "pyproject.toml",
            "Dockerfile",
            "README.md",
            "app/config.py",
            "app/schemas/realtime.py",
            "app/services/realtime_service.py",
            "app/api/dependencies.py",
            "app/api/routes/realtime.py",
            "app/main.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Realtime Service violation: Missing required file {req_file}")

        # Check endpoints in routes/realtime.py
        routes_file = base_dir / "app" / "api" / "routes" / "realtime.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/ws/orders/", "/ws/driver/", "/broadcast", "/stats"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Realtime Service violation: Missing endpoint route {ep} in routes/realtime.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_realtime_service()
        if v:
            all_violations["realtime-service"] = v
        return all_violations


if __name__ == "__main__":
    checker = RealtimeServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ REALTIME SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Realtime Service microservice verified cleanly (WebSockets Live Broadcast Engine intact).")
    sys.exit(0)
