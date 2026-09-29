"""Unit tests for application configuration."""

import os
import pytest
from pydantic import ValidationError


@pytest.mark.unit
def test_settings_loads_from_environment():
    """Settings must load DATABASE_URL from environment."""
    from app.core.config import get_settings

    # get_settings is cached; just verify it returns a Settings instance
    settings = get_settings()
    assert settings.DATABASE_URL is not None
    assert len(settings.DATABASE_URL) > 0


@pytest.mark.unit
def test_settings_app_name_default():
    """APP_NAME must default to 'incident-to-regression'."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.APP_NAME == "incident-to-regression"


@pytest.mark.unit
def test_settings_api_prefix():
    """API_PREFIX must be '/api/v1'."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.API_PREFIX == "/api/v1"


@pytest.mark.unit
def test_async_database_url_converts_postgresql_scheme():
    """ASYNC_DATABASE_URL must convert postgresql:// to postgresql+psycopg://."""
    # Test the conversion logic directly via a fresh Settings instance
    import importlib
    import app.core.config as config_module

    # Clear the lru_cache to force a fresh Settings load
    config_module.get_settings.cache_clear()

    original = os.environ.get("DATABASE_URL")
    try:
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
        os.environ["APP_ENV"] = "test"
        settings = config_module.Settings()  # type: ignore[call-arg]
        assert settings.ASYNC_DATABASE_URL.startswith("postgresql+psycopg://")
    finally:
        if original is not None:
            os.environ["DATABASE_URL"] = original
        # Restore the cached settings
        config_module.get_settings.cache_clear()
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_unit.db"
        os.environ["APP_ENV"] = "test"
        config_module.get_settings()  # re-populate cache


@pytest.mark.unit
def test_cors_origins_is_list():
    """CORS_ORIGINS must be a list."""
    from app.core.config import get_settings

    settings = get_settings()
    assert isinstance(settings.CORS_ORIGINS, list)
