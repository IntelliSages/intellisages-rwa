from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

# Importing this module registers the wider PostgresqlImpl in Alembic's
# dialect implementation registry before MigrationContext is configured.
from app.alembic_impl import ExtendedPostgresqlImpl  # noqa: F401
from app.database import (
    ensure_alembic_version_column_length,
    normalise_database_url,
)
from app.models import Base


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", normalise_database_url(configured_url))
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # Existing databases may already have a default VARCHAR(32) version
        # column. Widen that table before Alembic writes longer revision IDs.
        ensure_alembic_version_column_length(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
