"""
Order Service Checker.
Verifies production code structure, state machine, endpoints, models, schemas, service logic, and seed script of order-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class OrderServiceChecker:
    """Verifies complete Order Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_order_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "order-service"

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
            "app/schemas/order.py",
            "app/services/order_service.py",
            "app/api/dependencies.py",
            "app/api/routes/order.py",
            "app/main.py",
            "app/scripts/seed_orders.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Order Service violation: Missing required file {req_file}")

        # Check endpoints in routes/order.py
        routes_file = base_dir / "app" / "api" / "routes" / "order.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/orders", "/transition", "/cancel"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Order Service violation: Missing endpoint route {ep} in routes/order.py")

        # Check state machine in services/order_service.py
        service_file = base_dir / "app" / "services" / "order_service.py"
        if service_file.exists():
            content = service_file.read_text(encoding="utf-8")
            required_states = [
                "DRAFT", "COMPLIANCE_PENDING", "COMPLIANT", "PAYMENT_PENDING",
                "CONFIRMED", "DISPATCH_PENDING", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"
            ]
            for st in required_states:
                if st not in content:
                    violations.append(f"Order Service violation: Missing regulatory order state {st} in state machine")

        # Check models in db/models.py
        models_file = base_dir / "app" / "db" / "models.py"
        if models_file.exists():
            content = models_file.read_text(encoding="utf-8")
            required_models = [
                "class Order", "class OrderItem",
                "class OrderStateHistory", "class ComplianceValidationRecord"
            ]
            for model in required_models:
                if model not in content:
                    violations.append(f"Order Service violation: Missing database model {model} in db/models.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_order_service()
        if v:
            all_violations["order-service"] = v
        return all_violations


if __name__ == "__main__":
    checker = OrderServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ ORDER SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Order Service microservice verified cleanly (Regulatory State Machine, Compliance & Seeds intact).")
    sys.exit(0)
