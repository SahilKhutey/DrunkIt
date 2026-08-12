"""Email provider integration adapters."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import httpx

from faccp_common.integrations.base import IntegrationAdapter, IntegrationConfig
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class EmailAdapter(IntegrationAdapter):
    @abstractmethod
    async def send(
        self, to_email: str, subject: str, html_body: str, text_body: str | None = None,
        from_email: str | None = None, from_name: str | None = None, **kwargs
    ) -> dict[str, Any]:
        ...


class StubEmailAdapter(EmailAdapter):
    def __init__(self) -> None:
        super().__init__(IntegrationConfig(name="stub_email"))
    async def health_check(self) -> bool: return True
    async def send(self, to_email: str, subject: str, html_body: str, text_body: str | None = None, **kwargs) -> dict[str, Any]:
        logger.info("email.stub.sent", to=to_email, subject=subject)
        return {"status": "sent", "to": to_email, "provider": "stub"}


class SendGridEmailAdapter(EmailAdapter):
    def __init__(self, api_key: str, default_from_email: str, default_from_name: str = "FACCP") -> None:
        super().__init__(IntegrationConfig(name="sendgrid"))
        self._http = httpx.AsyncClient(
            base_url="https://api.sendgrid.com/v3",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        self.default_from_email = default_from_email
        self.default_from_name = default_from_name

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/scopes")
            return r.status_code == 200
        except Exception: return False

    async def send(
        self, to_email: str, subject: str, html_body: str, text_body: str | None = None,
        from_email: str | None = None, from_name: str | None = None, **kwargs
    ) -> dict[str, Any]:
        async def _do():
            r = await self._http.post("/mail/send", json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email or self.default_from_email, "name": from_name or self.default_from_name},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": text_body or ""},
                    {"type": "text/html", "value": html_body},
                ],
            })
            r.raise_for_status()
            return {"status": "sent", "to": to_email}
        return await self.call_with_retry(_do)
