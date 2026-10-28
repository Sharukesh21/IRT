"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "incident-to-regression"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Security & API Auth
    API_KEY_ENABLED: bool = False
    API_KEYS: list[str] = ["dev-admin-key", "ci-bot-key-secret"]
    RATE_LIMIT_PER_MINUTE: int = 120
    MAX_INGEST_PAYLOAD_BYTES: int = 1_000_000  # 1MB limit

    # Database (required)
    DATABASE_URL: Annotated[str, Field(min_length=1)]
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @computed_field  # type: ignore[misc]
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Convert DATABASE_URL to async-compatible URL for SQLAlchemy."""
        url = self.DATABASE_URL
        if url.startswith("postgresql+psycopg://"):
            return url
        if url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("sqlite"):
            # Allow SQLite for unit tests
            return url
        return url

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate environment name."""
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of: {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")
        return upper


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()  # type: ignore[call-arg]
