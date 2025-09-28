import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy import engine_from_config

from alembic import context

# The python path is now managed by `prepend_sys_path = .` in alembic.ini
from src.core.settings import get_settings

# Import all models to register them with SQLModel metadata
from src.db.models import User, AgentRun, OAuthAccount, Report  # noqa: F401
from sqlmodel import SQLModel

settings = get_settings()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use synchronous URL for offline mode
    sync_url = str(settings.DATABASE_URL).replace("+asyncpg", "")
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    alembic_config = config.get_section(config.config_ini_section)

    # Override the sqlalchemy.url with a synchronous version for Alembic
    sync_url = str(settings.DATABASE_URL).replace("+asyncpg", "")
    alembic_config["sqlalchemy.url"] = sync_url

    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
