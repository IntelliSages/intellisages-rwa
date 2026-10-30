from logging.config import fileConfig
import logging
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
logger = logging.getLogger("alembic.runtime.migration")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", normalise_database_url(configured_url))
target_metadata = Base.metadata

# These tables are the minimum schema required by the production catalogue.
# Checking them after upgrade prevents a healthy API process from starting
# against a different or incompletely migrated PostgreSQL database.
REQUIRED_POSTGRES_TABLES = (
    "alembic_version",
    "issuer_products",
    "issuers",
    "underlying_assets",
    "product_classifications",
)


def _log_postgresql_target(connection):
    target = connection.exec_driver_sql(
        """
        SELECT
            current_database() AS database_name,
            current_user AS database_user,
            current_schema() AS active_schema,
            current_setting('search_path') AS search_path,
            inet_server_addr()::text AS server_address,
            inet_server_port() AS server_port
        """
    ).mappings().one()
    logger.info(
        "Alembic PostgreSQL target: database=%s user=%s schema=%s "
        "search_path=%s server=%s port=%s",
        target["database_name"],
        target["database_user"],
        target["active_schema"],
        target["search_path"],
        target["server_address"],
        target["server_port"],
    )


def _verify_postgresql_schema(connection):
    version_table = connection.exec_driver_sql(
        "SELECT pg_catalog.to_regclass('alembic_version')"
    ).scalar_one_or_none()
    if version_table is None:
        raise RuntimeError(
            "Alembic migration completed without creating alembic_version. "
            "The PostgreSQL schema was not migrated; refusing to start the API."
        )

    revision = connection.exec_driver_sql(
        "SELECT version_num FROM alembic_version"
    ).scalar_one_or_none()
    if revision is None:
        raise RuntimeError(
            "Alembic migration completed but alembic_version contains no revision. "
            "Refusing to start the API against an unversioned PostgreSQL schema."
        )

    missing = connection.exec_driver_sql(
        """
        SELECT required.table_name
        FROM unnest(%s::text[]) AS required(table_name)
        WHERE pg_catalog.to_regclass(required.table_name) IS NULL
        ORDER BY required.table_name
        """,
        (list(REQUIRED_POSTGRES_TABLES),),
    ).scalars().all()
    if missing:
        raise RuntimeError(
            "Alembic recorded revision "
            + revision
            + " but the configured PostgreSQL database is missing required "
            "application tables: "
            + ", ".join(missing)
            + ". Check the Render DATABASE_URL resource and schema search_path."
        )

    logger.info(
        "Alembic schema verification passed: revision=%s required_tables=%s",
        revision,
        ", ".join(REQUIRED_POSTGRES_TABLES),
    )


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
        if connection.dialect.name == "postgresql":
            _log_postgresql_target(connection)

        # The target inspection above executes SELECT statements. SQLAlchemy 2.x
        # autobegins a transaction for those statements. Alembic treats an
        # already-active connection transaction as externally managed, so its
        # begin_transaction() context will not commit it. On a fresh database,
        # ensure_alembic_version_column_length() returns without committing.
        # Explicitly end any preflight transaction so Alembic owns the
        # migration transaction and commits it when the context exits.
        ensure_alembic_version_column_length(connection)
        if connection.in_transaction():
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

            # Verify before commit: a failed verification rolls back the
            # migration instead of persisting a partial or unusable schema.
            if connection.dialect.name == "postgresql":
                _verify_postgresql_schema(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
