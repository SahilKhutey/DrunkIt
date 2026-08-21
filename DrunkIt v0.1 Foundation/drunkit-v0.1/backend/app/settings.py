"""Configuration settings for DrunkIt v0.1 backend."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://drunkit:drunkit_dev@localhost:5432/drunkit"
    redis_url: str = "redis://localhost:6379/0"

    # Security & JWT Configuration
    jwt_secret: str = "drunkit_dev_jwt_secret_key_change_in_production_2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
