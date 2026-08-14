"""FACCP Common — Shared library for all Python services."""

from faccp_common.registry import ServiceEntry, ServiceRegistry, load_registry

__version__ = "0.1.0"

__all__ = [
    "ServiceEntry",
    "ServiceRegistry",
    "load_registry",
]

