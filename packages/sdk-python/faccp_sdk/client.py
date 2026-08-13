"""FACCP Async Python SDK Client."""

from __future__ import annotations

from typing import Any
import httpx


class FACCPClient:
    """Official Python SDK client for connecting to FACCP Platform API services."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._http = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=30.0)

    async def get_products(self, category: str | None = None) -> list[dict[str, Any]]:
        params = {"category": category} if category else {}
        res = await self._http.get("/api/v1/catalog/products", params=params)
        res.raise_for_status()
        return res.json().get("data", [])

    async def evaluate_policy(self, jurisdiction: str, context: dict[str, Any]) -> dict[str, Any]:
        res = await self._http.post("/api/v1/compliance/policies/evaluate", json={
            "jurisdiction_code": jurisdiction,
            "context": context,
        })
        res.raise_for_status()
        return res.json().get("data", {})

    async def close(self) -> None:
        await self._http.aclose()
