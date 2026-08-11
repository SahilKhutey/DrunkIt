from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException

from app.domain.marketplace import (
    APIKeyIssuer,
    MarketplaceCatalog,
    PlanLimit,
    Subscription,
    UsageEvent,
    UsageMeter,
)
from app.schemas import (
    APIKeyResponse,
    CreateAPIKeyRequest,
    CreateSubscriptionRequest,
    UsageDecisionRequest,
    UsageEventRequest,
)


class DeveloperPortalState:
    def __init__(self) -> None:
        secret = os.environ.get("FACCP_DEVELOPER_PORTAL_SECRET", "local-dev-secret")
        self.catalog = MarketplaceCatalog()
        self.key_issuer = APIKeyIssuer(secret=secret)
        self.usage = UsageMeter()
        self.subscriptions: dict[tuple[str, str], Subscription] = {}


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Developer Portal", version="0.1.0")
    state = DeveloperPortalState()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "faccp-developer-portal"}

    @app.get("/api/v1/marketplace/products")
    async def list_products() -> dict[str, Any]:
        return {"items": state.catalog.list_public()}

    @app.post("/api/v1/developer-apps/keys", status_code=201)
    async def create_api_key(payload: CreateAPIKeyRequest) -> APIKeyResponse:
        material = state.key_issuer.issue(payload.app_id, payload.environment)
        return APIKeyResponse(
            key_id=material.key_id,
            plaintext_key=material.plaintext_key,
            key_hash=material.key_hash,
            prefix=material.prefix,
            created_at=material.created_at,
        )

    @app.post("/api/v1/subscriptions", status_code=201)
    async def create_subscription(payload: CreateSubscriptionRequest) -> dict[str, Any]:
        try:
            state.catalog.get(payload.product_code)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        limits = PlanLimit(
            requests_per_minute=payload.limits.requests_per_minute,
            requests_per_day=payload.limits.requests_per_day,
            requests_per_month=payload.limits.requests_per_month,
            burst=payload.limits.burst,
        )
        subscription = Subscription(
            developer_id=payload.developer_id,
            app_id=payload.app_id,
            product_code=payload.product_code,
            plan_code=payload.plan_code,
            status="active",
            limits=limits,
            monthly_price=Decimal(payload.monthly_price),
            currency=payload.currency,
        )
        state.subscriptions[(subscription.app_id, subscription.product_code)] = subscription
        return {
            "developer_id": subscription.developer_id,
            "app_id": subscription.app_id,
            "product_code": subscription.product_code,
            "plan_code": subscription.plan_code,
            "status": subscription.status,
            "limits": {
                "requests_per_minute": limits.requests_per_minute,
                "requests_per_day": limits.requests_per_day,
                "requests_per_month": limits.requests_per_month,
                "burst": limits.burst,
            },
            "monthly_price": str(subscription.monthly_price),
            "currency": subscription.currency,
        }

    @app.post("/api/v1/usage/events", status_code=202)
    async def record_usage(payload: UsageEventRequest) -> dict[str, str]:
        state.usage.record(
            UsageEvent(
                app_id=payload.app_id,
                product_code=payload.product_code,
                endpoint=payload.endpoint,
                status_code=payload.status_code,
                latency_ms=payload.latency_ms,
                occurred_at=payload.occurred_at or UsageEvent(
                    payload.app_id,
                    payload.product_code,
                    payload.endpoint,
                    payload.status_code,
                    payload.latency_ms,
                ).occurred_at,
            )
        )
        return {"status": "accepted"}

    @app.post("/api/v1/usage/decisions")
    async def usage_decision(payload: UsageDecisionRequest) -> dict[str, Any]:
        subscription = state.subscriptions.get((payload.app_id, payload.product_code))
        if subscription is None:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return state.usage.allowed(
            subscription,
            window=payload.window,
            window_start=payload.window_start,
            now=payload.now,
        )

    @app.get("/api/v1/developer-apps/{app_id}/usage-summary")
    async def usage_summary(app_id: str) -> dict[str, Any]:
        return {"app_id": app_id, "products": state.usage.summarize_by_product(app_id)}

    return app


app = create_app()
