"""
Tenant context for multi-tenancy support.
Provides request-scoped tenant context that propagates through service calls, ensuring data isolation.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any


@dataclass
class TenantContext:
    tenant_id: str
    tenant_type: str  # organization | consumer | admin | system
    jurisdiction: str | None = None
    scopes: list[str] = None  # type: ignore
    isolation_level: str = "row"  # row | schema | database
    parent_tenant: str | None = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


_current_tenant: ContextVar[TenantContext | None] = ContextVar("current_tenant", default=None)


def set_tenant(tenant: TenantContext) -> None:
    _current_tenant.set(tenant)


def get_current_tenant() -> TenantContext | None:
    return _current_tenant.get()


def clear_tenant() -> None:
    _current_tenant.set(None)


def require_tenant() -> TenantContext:
    tenant = get_current_tenant()
    if tenant is None:
        raise ValueError("No tenant context set for this request")
    return tenant
