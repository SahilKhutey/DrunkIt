"""CLI script to export registry metadata to JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from faccp_platform.registry.loader import ServiceRegistry


def main() -> int:
    registry = ServiceRegistry()
    services_dict = {}
    for service in registry.services():
        services_dict[service.name] = {
            "name": service.name,
            "type": service.type.value,
            "runtime": service.runtime.value,
            "host": service.host,
            "port": service.port,
            "base_url": service.base_url,
            "health_url": service.health_url,
            "readiness_url": service.readiness_url,
            "dependencies": list(service.dependencies),
        }

    output_path = ROOT / "services" / "services.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"version": "1.0.0", "services": services_dict}, f, indent=2)

    print(f"Exported {len(services_dict)} services to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
