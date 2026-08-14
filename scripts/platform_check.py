"""CLI platform validation script."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from faccp_platform.health.checks import check_service_port
from faccp_platform.registry.loader import ServiceRegistry

REGISTRY_PATH = ROOT / "faccp_platform" / "registry" / "registry.yaml"


def main() -> int:
    print("=" * 60)
    print("FACCP PLATFORM VALIDATION")
    print("=" * 60)

    registry = ServiceRegistry(REGISTRY_PATH)
    errors = registry.validate()

    if errors:
        print("\nREGISTRY ERRORS\n")
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("\nRegistry validation: PASS")
    print("\nService ports:\n")

    failed = False
    for service in registry.services():
        result = check_service_port(service)
        if result.healthy:
            print(
                f"[PASS] {service.name:<20} {service.host}:{service.port} {result.latency_ms} ms"
            )
        else:
            failed = True
            print(
                f"[WARN] {service.name:<20} {service.host}:{service.port} {result.error}"
            )

    print("\n" + "=" * 60)
    if failed:
        print("PLATFORM STATUS: PARTIALLY AVAILABLE")
    else:
        print("PLATFORM STATUS: ALL SERVICES AVAILABLE")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
