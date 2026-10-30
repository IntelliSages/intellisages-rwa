from logging.config import fileConfig
import os

from alembic import context
from alembic.ddl.impl import DefaultImpl
from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, String, Table, engine_from_config, pool

from app.database import (
    ALEMBIC_VERSION_NUM_LENGTH,
    ensure_alembic_version_column_length,
    normalise_database_url,
)
from app.models import Base


class ExtendedVersionTableImpl(DefaultImpl):
    """Alembic implementation with a revision column sized for long IDs."""

    __dialect__ = "default"

    def version_table_impl(
        self,
        *,
        version_table: str,
        version_table_schema: str | None,
        version_table_pk: bool,
        **kw,
    ) -> Table:
        table = Table(
            version_table,
            MetaData(),
            Column("version_num", String(ALEMBIC_VERSION_NUM_LENGTH), nullable=False),
            schema=version_table_schema,
        )
        if version_table_pk:
            table.append_constraint(
                PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc")
            )
        return table


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
        version_table_impl=ExtendedVersionTableImpl,
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
        ensure_alembic_version_column_length(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_impl=ExtendedVersionTableImpl,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
