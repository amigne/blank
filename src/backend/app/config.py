"""Application configuration loaded from environment variables."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    """Typed application settings sourced from environment variables.

    All secrets must be provided via environment — never committed to the repo.
    Call ``check_secrets()`` at startup to refuse starting with placeholder values
    """

    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets"
    )

    # ── Environment ────────────────────────────────────────────────────
    environment: str = "production"

    # ── Logging ───────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Health ────────────────────────────────────────────────────────
    health_full_token: SecretStr | None = Field(
        default=None, min_length=32, max_length=128
    )

    # ── CORS ──────────────────────────────────────────────────────────
    # cors_origin: str

    # ── Database ──────────────────────────────────────────────────────
    database_host: str
    database_port: int = 5432
    database_user: str
    database_password: SecretStr = Field(min_length=8, max_length=128)
    database_name: str

    # ── API ────────────────────────────────────────────────────────────
    docs_url: str | None = None
    redoc_url: str | None = None
    openapi_url: str | None = None

    @property
    def database_url(self) -> URL:
        """Return the SQLAlchemy database URL for asyncpg."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.database_user,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


settings = Settings()
