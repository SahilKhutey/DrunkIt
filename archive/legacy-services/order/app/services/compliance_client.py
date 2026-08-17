"""HTTP Compliance Client."""

from __future__ import annotations

import httpx


class ComplianceClient:
    """HTTP client communicating with Compliance Service API boundary."""

    def __init__(self, base_url: str = "http://localhost:8011") -> None:
        self.base_url = base_url.rstrip("/")

    async def evaluate(self, payload: dict) -> dict:
        """Post eligibility evaluation request to Compliance Service."""
        url = f"{self.base_url}/eligibility/evaluate"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
