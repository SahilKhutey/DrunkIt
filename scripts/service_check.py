"""CLI single service verification script."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from faccp_platform.health.checks import check_service_port
from faccp_platform.registry.loader import ServiceRegistry


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/service_check.py <service-name>")
        return 1

    service_name = sys.argv[1]
    registry = ServiceRegistry()
    try:
        service = registry.get(service_name)
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    print(f"Service: {service.name}")
    print(f"  Type: {service.type.value}")
    print(f"  Runtime: {service.runtime.value}")
    print(f"  URL: {service.base_url}")
    print(f"  Health URL: {service.health_url}")
    print(f"  Readiness URL: {service.readiness_url}")
    print(f"  Dependencies: {', '.join(service.dependencies) or 'none'}")

    result = check_service_port(service)
    if result.healthy:
        print(f"  Status: HEALTHY ({result.latency_ms} ms)")
        return 0
    else:
        print(f"  Status: UNHEALTHY ({result.error})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
