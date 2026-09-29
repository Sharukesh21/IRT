"""Alembic environment configuration for async SQLAlchemy.

Reads the database URL from application Settings (not from alembic.ini),
ensuring a single source of truth for all database configuration.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# This import makes all models visible to Alembic's autogenerate
from app.db.base import Base
import app.db.models  # noqa: F401  — side-effect import registers all models

from app.core.config import get_settings

# ---------------------------------------------------------------------------
# Alembic Config object (provides access to values in alembic.ini)
# ---------------------------------------------------------------------------

config = context.config

# Configure Python logging from alembic.ini if a logging section is present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Set the database URL from application settings
# ---------------------------------------------------------------------------

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.ASYNC_DATABASE_URL)

# Target metadata for autogenerate support
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — generate SQL without connecting to the database
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — run migrations against a live database
# ---------------------------------------------------------------------------


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within a transaction."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (against a live database)."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
