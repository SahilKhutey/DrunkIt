from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):

    database_url: str = (
        "postgresql+asyncpg://"
        "platform:platform_password@"
        "localhost:5432/platform"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = DatabaseSettings()
