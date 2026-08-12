"""Payment gateway integration adapters."""

from __future__ import annotations

import secrets
from abc import abstractmethod
from typing import Any

import httpx

from faccp_common.integrations.base import IntegrationAdapter, IntegrationConfig
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class PaymentGatewayAdapter(IntegrationAdapter):

    @abstractmethod
    async def create_intent(self, amount_cents: int, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def confirm_intent(self, intent_id: str, payment_method: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def capture(self, intent_id: str, amount_cents: int | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def refund(self, transaction_id: str, amount_cents: int, reason: str) -> dict[str, Any]:
        ...


class StubPaymentAdapter(PaymentGatewayAdapter):

    def __init__(self) -> None:
        super().__init__(IntegrationConfig(name="stub_payment"))
        self._intents: dict[str, dict[str, Any]] = {}

    async def health_check(self) -> bool: return True

    async def create_intent(self, amount_cents: int, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        intent_id = f"pi_stub_{secrets.token_hex(12)}"
        self._intents[intent_id] = {
            "id": intent_id, "amount": amount_cents, "currency": currency,
            "status": "requires_payment_method", "metadata": metadata,
            "client_secret": f"{intent_id}_secret_{secrets.token_hex(8)}",
        }
        return self._intents[intent_id]

    async def confirm_intent(self, intent_id: str, payment_method: dict[str, Any]) -> dict[str, Any]:
        if intent_id in self._intents:
            self._intents[intent_id]["status"] = "requires_capture"
            self._intents[intent_id]["payment_method"] = payment_method
        return self._intents.get(intent_id, {"error": "not_found"})

    async def capture(self, intent_id: str, amount_cents: int | None = None) -> dict[str, Any]:
        if intent_id in self._intents:
            self._intents[intent_id]["status"] = "succeeded"
        return self._intents.get(intent_id, {"error": "not_found"})

    async def refund(self, transaction_id: str, amount_cents: int, reason: str) -> dict[str, Any]:
        return {
            "id": f"re_stub_{secrets.token_hex(12)}",
            "transaction_id": transaction_id, "amount": amount_cents,
            "status": "succeeded", "reason": reason,
        }


class RazorpayPaymentAdapter(PaymentGatewayAdapter):

    def __init__(self, key_id: str, key_secret: str) -> None:
        super().__init__(IntegrationConfig(name="razorpay"))
        self._http = httpx.AsyncClient(
            base_url="https://api.razorpay.com/v1",
            auth=(key_id, key_secret),
            timeout=30.0,
        )

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/payments", params={"count": 1})
            return r.status_code == 200
        except Exception:
            return False

    async def create_intent(self, amount_cents: int, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        async def _do():
            r = await self._http.post(
                "/orders",
                json={"amount": amount_cents, "currency": currency, "notes": metadata},
            )
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)

    async def confirm_intent(self, intent_id: str, payment_method: dict[str, Any]) -> dict[str, Any]:
        async def _do():
            r = await self._http.get(f"/orders/{intent_id}/payments")
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)

    async def capture(self, intent_id: str, amount_cents: int | None = None) -> dict[str, Any]:
        async def _do():
            r = await self._http.post(f"/payments/{intent_id}/capture", json={"amount": amount_cents} if amount_cents else {})
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)

    async def refund(self, transaction_id: str, amount_cents: int, reason: str) -> dict[str, Any]:
        async def _do():
            r = await self._http.post(
                f"/payments/{transaction_id}/refund",
                json={"amount": amount_cents, "speed": "optimum", "notes": {"reason": reason}},
            )
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)
