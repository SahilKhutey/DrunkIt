from __future__ import annotations

from functools import lru_cache
from faccp_common.config import BaseServiceSettings


class IdentitySettings(BaseServiceSettings):
    service_name: str = "identity-service"
    port: int = 8001
    database_url: str = "postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_identity"
    jwt_secret: str = "faccp-identity-vault-super-secret-key-32bytes"
    field_encryption_key: str = "dGVzdC1mZXJuZXQtS2V5LTMyLWJ5dGVzLXNlY3VyZSE="  # Base64 32 bytes


@lru_cache(maxsize=1)
def get_settings() -> IdentitySettings:
    return IdentitySettings()
