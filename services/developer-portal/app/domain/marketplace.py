from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal

PlanCadence = Literal["monthly", "annual"]
UsageWindow = Literal["minute", "day", "month"]


@dataclass(frozen=True)
class PlanLimit:
    requests_per_minute: int
    requests_per_day: int
    requests_per_month: int
    burst: int = 0

    def allowance_for(self, window: UsageWindow) -> int:
        if window == "minute":
            return self.requests_per_minute + self.burst
        if window == "day":
            return self.requests_per_day
        return self.requests_per_month


@dataclass(frozen=True)
class APIProduct:
    code: str
    name: str
    description: str
    base_path: str
    openapi_tag: str
    scopes: tuple[str, ...]
    sandbox_enabled: bool = True
    regulator_sensitive: bool = False


@dataclass(frozen=True)
class Subscription:
    developer_id: str
    app_id: str
    product_code: str
    plan_code: str
    status: Literal["trial", "active", "suspended", "cancelled"]
    limits: PlanLimit
    monthly_price: Decimal
    currency: str = "INR"
    cadence: PlanCadence = "monthly"

    def can_call(self) -> bool:
        return self.status in {"trial", "active"}


@dataclass(frozen=True)
class APIKeyMaterial:
    key_id: str
    plaintext_key: str
    key_hash: str
    prefix: str
    created_at: datetime


@dataclass(frozen=True)
class UsageEvent:
    app_id: str
    product_code: str
    endpoint: str
    status_code: int
    latency_ms: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MarketplaceCatalog:
    def __init__(self, products: list[APIProduct] | None = None) -> None:
        self._products: dict[str, APIProduct] = {}
        for product in products or default_products():
            self.add_product(product)

    def add_product(self, product: APIProduct) -> None:
        if not product.code or not product.base_path.startswith("/"):
            raise ValueError("API product must have a code and absolute base path")
        self._products[product.code] = product

    def get(self, code: str) -> APIProduct:
        try:
            return self._products[code]
        except KeyError as exc:
            raise KeyError(f"Unknown API product: {code}") from exc

    def list_public(self) -> list[dict[str, Any]]:
        return [
            {
                "code": product.code,
                "name": product.name,
                "description": product.description,
                "base_path": product.base_path,
                "scopes": list(product.scopes),
                "sandbox_enabled": product.sandbox_enabled,
                "regulator_sensitive": product.regulator_sensitive,
            }
            for product in sorted(self._products.values(), key=lambda item: item.code)
        ]

    def scopes_for_products(self, product_codes: list[str]) -> set[str]:
        scopes: set[str] = set()
        for code in product_codes:
            scopes.update(self.get(code).scopes)
        return scopes


class APIKeyIssuer:
    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("API key issuer secret is required")
        self._secret = secret.encode("utf-8")

    def issue(self, app_id: str, environment: Literal["sandbox", "production"]) -> APIKeyMaterial:
        key_id = secrets.token_hex(8)
        random_part = secrets.token_urlsafe(32)
        plaintext = f"faccp_{environment}_{key_id}_{random_part}"
        return APIKeyMaterial(
            key_id=key_id,
            plaintext_key=plaintext,
            key_hash=self.hash_key(plaintext),
            prefix="_".join(plaintext.split("_")[:3]),
            created_at=datetime.now(timezone.utc),
        )

    def hash_key(self, plaintext_key: str) -> str:
        return hmac.new(self._secret, plaintext_key.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, plaintext_key: str, expected_hash: str) -> bool:
        return hmac.compare_digest(self.hash_key(plaintext_key), expected_hash)


class UsageMeter:
    def __init__(self) -> None:
        self._events: list[UsageEvent] = []

    def record(self, event: UsageEvent) -> None:
        self._events.append(event)

    def count(
        self,
        *,
        app_id: str,
        product_code: str,
        since: datetime,
        until: datetime | None = None,
    ) -> int:
        until = until or datetime.now(timezone.utc)
        return sum(
            1
            for event in self._events
            if event.app_id == app_id
            and event.product_code == product_code
            and since <= event.occurred_at <= until
        )

    def allowed(
        self,
        subscription: Subscription,
        *,
        window: UsageWindow,
        window_start: datetime,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        if not subscription.can_call():
            return {"allowed": False, "reason": f"subscription_{subscription.status}", "remaining": 0}
        used = self.count(
            app_id=subscription.app_id,
            product_code=subscription.product_code,
            since=window_start,
            until=now,
        )
        limit = subscription.limits.allowance_for(window)
        return {
            "allowed": used < limit,
            "used": used,
            "limit": limit,
            "remaining": max(limit - used, 0),
            "window": window,
        }

    def summarize_by_product(self, app_id: str) -> dict[str, dict[str, Any]]:
        summary: dict[str, dict[str, Any]] = {}
        for event in self._events:
            if event.app_id != app_id:
                continue
            row = summary.setdefault(
                event.product_code,
                {"requests": 0, "errors": 0, "total_latency_ms": 0},
            )
            row["requests"] += 1
            row["total_latency_ms"] += event.latency_ms
            if event.status_code >= 400:
                row["errors"] += 1
        for row in summary.values():
            row["avg_latency_ms"] = row["total_latency_ms"] / row["requests"]
            row["error_rate"] = row["errors"] / row["requests"]
        return summary


def default_products() -> list[APIProduct]:
    return [
        APIProduct(
            code="catalog",
            name="Product Catalog API",
            description="Search regulated alcohol catalogs with jurisdiction-aware availability.",
            base_path="/api/v1/catalog",
            openapi_tag="Catalog",
            scopes=("catalog:read",),
        ),
        APIProduct(
            code="orders",
            name="Order Orchestration API",
            description="Create carts, submit orders, and track state transitions.",
            base_path="/api/v1/orders",
            openapi_tag="Orders",
            scopes=("orders:read", "orders:write"),
            regulator_sensitive=True,
        ),
        APIProduct(
            code="verification",
            name="Age Verification API",
            description="Run claim-based age and identity verification workflows.",
            base_path="/api/v1/verification",
            openapi_tag="Verification",
            scopes=("verification:read", "verification:write"),
            regulator_sensitive=True,
        ),
        APIProduct(
            code="compliance",
            name="Compliance Decision API",
            description="Evaluate jurisdiction policies before sale, pickup, or delivery.",
            base_path="/api/v1/compliance",
            openapi_tag="Compliance",
            scopes=("compliance:evaluate",),
            regulator_sensitive=True,
        ),
    ]
