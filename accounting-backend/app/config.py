"""Runtime settings for the standalone accounting backend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven host settings.

    The accounting package uses `ACCOUNTING_` variables. Admin auth is owned by
    this host service and deliberately uses separate `ADMIN_` variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    accounting_api_prefix: str = Field(default="/api/accounting", validation_alias="ACCOUNTING_API_PREFIX")
    backend_host: str = Field(default="127.0.0.1", validation_alias="ACCOUNTING_BACKEND_HOST")
    backend_port: int = Field(default=8000, validation_alias="ACCOUNTING_BACKEND_PORT")

    accounting_database_url: str = Field(
        default="sqlite:///./data/accounting.db",
        validation_alias="ACCOUNTING_DATABASE_URL",
    )
    accounting_storage_path: Path = Field(
        default=Path("./data/accounting-storage"),
        validation_alias="ACCOUNTING_STORAGE_PATH",
    )

    admin_username: str = Field(default="", validation_alias="ADMIN_USERNAME")
    admin_password_hash: str = Field(default="", validation_alias="ADMIN_PASSWORD_HASH")
    admin_display_name: str = Field(default="Accounting Admin", validation_alias="ADMIN_DISPLAY_NAME")
    admin_email: str = Field(default="", validation_alias="ADMIN_EMAIL")
    secret_key: str = Field(default="", validation_alias="SECRET_KEY")
    admin_token_ttl_seconds: int = Field(default=8 * 60 * 60, validation_alias="ADMIN_TOKEN_TTL_SECONDS")
    admin_allowed_origins: str = Field(
        default="http://localhost:5174,http://127.0.0.1:5174",
        validation_alias="ADMIN_ALLOWED_ORIGINS",
    )

    accounting_email_provider: Literal["console", "smtp", "disabled"] = Field(
        default="console",
        validation_alias="ACCOUNTING_EMAIL_PROVIDER",
    )
    accounting_email_from: str = Field(default="", validation_alias="ACCOUNTING_EMAIL_FROM")
    accounting_smtp_host: str = Field(default="", validation_alias="ACCOUNTING_SMTP_HOST")
    accounting_smtp_port: int = Field(default=587, validation_alias="ACCOUNTING_SMTP_PORT")
    accounting_smtp_user: str = Field(default="", validation_alias="ACCOUNTING_SMTP_USER")
    accounting_smtp_password: str = Field(default="", validation_alias="ACCOUNTING_SMTP_PASSWORD")
    accounting_smtp_use_tls: bool = Field(default=True, validation_alias="ACCOUNTING_SMTP_USE_TLS")
    accounting_ares_provider: Literal["mock", "real"] = Field(
        default="mock",
        validation_alias="ACCOUNTING_ARES_PROVIDER",
    )

    @field_validator("accounting_storage_path", mode="before")
    @classmethod
    def _coerce_storage_path(cls, value: object) -> Path:
        if isinstance(value, Path):
            return value
        return Path(str(value))

    def parsed_admin_origins(self) -> list[str]:
        origins = [item.strip() for item in self.admin_allowed_origins.split(",") if item.strip()]
        if self.app_env.lower() == "production" and "*" in origins:
            raise ValueError("ADMIN_ALLOWED_ORIGINS cannot contain * in production.")
        return origins

    def ensure_storage_directory(self) -> Path:
        path = self.accounting_storage_path.expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def auth_configured(self) -> bool:
        return bool(self.admin_username.strip() and self.admin_password_hash.strip() and self.secret_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
