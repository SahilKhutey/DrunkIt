"""
Service-to-Service Identity & Auth Token Generator (§14.8).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
import jwt


class ServiceIdentity:
    """Identity for non-human actors (services, background systems)."""

    def __init__(
        self,
        service_name: str,
        environment: str = "local",
        version: str = "1.0.0",
        instance_id: str | None = None,
        secret_key: str = "service_jwt_secret_placeholder_32bytes!",

    ) -> None:
        self.service_name = service_name
        self.environment = environment
        self.version = version
        self.instance_id = instance_id or f"inst_{uuid.uuid4().hex[:8]}"
        self.secret_key = secret_key

    def get_token(self, ttl_minutes: int = 5) -> str:
        """Get a signed JWT for service-to-service authentication."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": f"service:{self.service_name}",
            "iss": "faccp-platform",
            "aud": "faccp-internal",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
            "jti": str(uuid.uuid4()),
            "type": "service",
            "service_name": self.service_name,
            "environment": self.environment,
            "version": self.version,
            "instance_id": self.instance_id,
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
