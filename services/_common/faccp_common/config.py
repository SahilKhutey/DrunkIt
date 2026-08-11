from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """Base configuration inherited by every service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    # ---------- Service identity ----------
    service_name: str = "faccp-service"
    service_version: str = "0.1.0"
    environment: Literal["local", "development", "staging", "production", "test"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    debug: bool = False

    # ---------- Server ----------
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    cors_allowed_origins: str = "http://localhost:3000"

    # ---------- Database ----------
    database_url: str = Field(
        default="postgresql+asyncpg://faccp_admin:faccp_password@localhost:5432/faccp_identity"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_echo: bool = False

    # ---------- Redis ----------
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    redis_max_connections: int = 50

    # ---------- Kafka ----------
    kafka_brokers: str = "localhost:9092"
    kafka_client_id: str = "faccp-service"
    kafka_consumer_group: str = "faccp-service-group"
    kafka_security_protocol: Literal["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"] = "PLAINTEXT"

    # ---------- JWT / Auth ----------
    jwt_secret: str = "faccp-identity-vault-super-secret-key-32bytes"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "faccp-platform"
    jwt_audience: str = "faccp-api"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ---------- Encryption ----------
    field_encryption_key: str = "change-me-32-byte-key-please-replace"
    kms_provider: Literal["local", "aws", "vault"] = "local"

    # ---------- Object Storage ----------
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_access_key: str = "faccp"
    object_storage_secret_key: str = "faccp_dev_password"
    object_storage_bucket: str = "faccp-documents"
    object_storage_secure: bool = False

    # ---------- Inter-service URLs ----------
    identity_service_url: str = "http://localhost:8001"
    consumer_service_url: str = "http://localhost:8002"
    retailer_service_url: str = "http://localhost:8003"
    catalog_service_url: str = "http://localhost:8004"
    inventory_service_url: str = "http://localhost:8005"
    order_service_url: str = "http://localhost:8006"
    compliance_service_url: str = "http://localhost:8007"
    audit_service_url: str = "http://localhost:8008"
    risk_service_url: str = "http://localhost:8009"
    verification_service_url: str = "http://localhost:8010"
    delivery_service_url: str = "http://localhost:8011"
    notification_service_url: str = "http://localhost:8012"

    # ---------- Observability ----------
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "faccp-service"
    enable_tracing: bool = True
    enable_metrics: bool = True

    # ---------- Feature flags ----------
    feature_mfa_enforced: bool = False
    feature_kyc_required: bool = True
    feature_policy_engine_enabled: bool = True

    # ---------- Rate limiting ----------
    rate_limit_per_minute: int = 120
    rate_limit_burst: int = 200

    @field_validator("cors_allowed_origins")
    @classmethod
    def _parse_cors(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def kafka_bootstrap_servers(self) -> list[str]:
        return [b.strip() for b in self.kafka_brokers.split(",") if b.strip()]


@lru_cache(maxsize=1)
def get_settings() -> BaseServiceSettings:
    """Cached settings accessor."""
    return BaseServiceSettings()
