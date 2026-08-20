"""
Root conftest — loaded by pytest before any test collection.

Legacy Service Path Bridge
--------------------------
During the P0-A canonicalization (2026-08-16), unregistered legacy service
directories were moved from services/<name>/ to archive/legacy-services/<name>/.

Tests that import `services.compliance`, `services.payment`, `services.order`,
`services.fulfillment`, `services.risk`, etc. continue to work because this
conftest injects archive/legacy-services/ into the `services` namespace package
search path via pytest_configure (fired before collection).

TODO (P1): Rewrite all `from services.<legacy_name>` imports to the canonical
           registered service paths (services/<name>-service/) and remove the
           bridge in pytest_configure() below.
"""

from __future__ import annotations

import os
import pathlib
import sys
import types

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

_REPO_ROOT = pathlib.Path(__file__).parent
_ARCHIVE_LEGACY = _REPO_ROOT / "archive" / "legacy-services"


def pytest_configure(config):
    """
    Called after all plugins are loaded and command-line options parsed —
    before any test collection begins.

    Injects archive/legacy-services/ into the `services` namespace package
    so that `from services.payment.app.schemas.payment import ...` etc.
    continues to resolve from the archive location.
    """
    if not _ARCHIVE_LEGACY.exists():
        return

    services_path = _REPO_ROOT / "services"

    if "services" not in sys.modules:
        # Create a namespace package for `services` that searches both
        # the real services/ directory and the archive.
        mod = types.ModuleType("services")
        mod.__path__ = [str(services_path), str(_ARCHIVE_LEGACY)]
        mod.__package__ = "services"
        mod.__spec__ = None
        sys.modules["services"] = mod
    else:
        # `services` was already imported (e.g. by a prior conftest).
        # Append the archive to its search path.
        svc = sys.modules["services"]
        if hasattr(svc, "__path__"):
            existing = list(svc.__path__)
            if str(_ARCHIVE_LEGACY) not in existing:
                svc.__path__ = existing + [str(_ARCHIVE_LEGACY)]
