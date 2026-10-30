from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models import Base
from app.database import (
    ALEMBIC_VERSION_NUM_LENGTH,
    ensure_alembic_version_column_length,
    normalise_database_url,
)

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
        version_num_length=ALEMBIC_VERSION_NUM_LENGTH,
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
        # Existing databases may already have Alembic's default VARCHAR(32)
        # version column. Widen it before Alembic writes longer revision IDs.
        ensure_alembic_version_column_length(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_num_length=ALEMBIC_VERSION_NUM_LENGTH,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
