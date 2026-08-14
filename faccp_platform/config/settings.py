"""Platform configuration settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from .environments import Environment


class PlatformSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FACCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    secret_key: str = "faccp_platform_default_secret_key_change_in_prod"
    platform_name: str = "FACCP Platform Core"
    platform_version: str = "0.1.0"

    # Infrastructure Defaults
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "faccp"
    postgres_password: str = "faccp_dev_password_change_in_production"
    postgres_db: str = "faccp"

    redis_host: str = "localhost"
    redis_port: int = 6379

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "faccp-platform"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_request_timeout_ms: int = 30000

    # Security Defaults
    access_token_secret: str = "development-access-secret-minimum-32-bytes-long"
    refresh_token_secret: str = "development-refresh-secret-minimum-32-bytes-long"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    password_min_length: int = 12
    max_login_attempts: int = 5
    login_lockout_minutes: int = 15

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


_platform_settings: PlatformSettings | None = None


def get_platform_settings() -> PlatformSettings:
    global _platform_settings
    if _platform_settings is None:
        _platform_settings = PlatformSettings()
    return _platform_settings


get_settings = get_platform_settings

