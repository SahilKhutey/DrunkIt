from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.config import get_settings

settings = get_settings()

SERVICE_ROUTES = {
    "/api/v1/auth": settings.identity_service_url,
    "/api/v1/consumer": settings.consumer_service_url,
    "/api/v1/retailer": settings.retailer_service_url,
    "/api/v1/catalog": settings.catalog_service_url,
    "/api/v1/inventory": settings.inventory_service_url,
    "/api/v1/orders": settings.order_service_url,
    "/api/v1/compliance": settings.compliance_service_url,
    "/api/v1/audit": settings.audit_service_url,
    "/api/v1/risk": settings.risk_service_url,
    "/api/v1/verification": settings.verification_service_url,
    "/api/v1/delivery": settings.delivery_service_url,
    "/api/v1/notifications": settings.notification_service_url,
    "/api/v1/payments": settings.payment_service_url,
    "/api/v1/pricing": settings.pricing_service_url,
    "/api/v1/analytics": settings.analytics_service_url,
    "/api/v1/realtime": settings.realtime_service_url,
    "/api/v1/recommendations": settings.recommendation_service_url,
    "/api/v1/whitelabel": settings.whitelabel_service_url,
    "/api/v1/reports": settings.reporting_service_url,
    "/api/v1/support": settings.support_service_url,
}



client: httpx.AsyncClient | None = None



@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    global client
    client = httpx.AsyncClient(timeout=30.0)
    yield
    await client.aclose()


app = FastAPI(title="FACCP API Gateway", version=settings.service_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"])
async def proxy_request(request: Request, path: str) -> Response:
    global client
    assert client is not None

    full_path = f"/{path}"
    target_base = None

    for prefix, target_url in SERVICE_ROUTES.items():
        if full_path.startswith(prefix):
            target_base = target_url
            break

    if not target_base:
        return Response(content='{"error": {"code": "NOT_FOUND", "message": "Route not matched"}}', status_code=404, media_type="application/json")

    url = f"{target_base}{full_path}"
    if request.url.query:
        url += f"?{request.url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    content = await request.body()

    rp_req = client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=content,
    )
    rp_resp = await client.send(rp_req)

    return Response(
        content=rp_resp.content,
        status_code=rp_resp.status_code,
        headers=dict(rp_resp.headers),
        media_type=rp_resp.headers.get("content-type"),
    )
