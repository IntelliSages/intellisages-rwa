from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


ALEMBIC_VERSION_NUM_LENGTH = 128


def normalise_database_url(value: str) -> str:
    """Use the explicitly installed psycopg v3 driver for PostgreSQL URLs."""
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value.removeprefix("postgres://")
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value.removeprefix("postgresql://")
    return value


def commit_pre_migration_transaction(connection) -> None:
    """Close SQLAlchemy's autobegun transaction before Alembic takes ownership.

    Database inspection queries run before Alembic starts. Under SQLAlchemy 2.x,
    those queries autobegin a transaction; Alembic will not commit a transaction
    it did not create.
    """
    if connection.in_transaction():
        connection.commit()


def ensure_alembic_version_column_length(connection) -> bool:
    """Widen an existing Alembic version table before version updates.

    Alembic 1.16.1 hardcodes String(32) in its default version-table
    implementation. This helper widens an already-created table. Fresh
    databases are handled by the custom Alembic DefaultImpl in migrations/env.py.
    """
    if connection.dialect.name != "postgresql":
        return False

    schema = connection.exec_driver_sql(
        """
        SELECT namespace.nspname
        FROM pg_catalog.pg_class AS relation
        JOIN pg_catalog.pg_namespace AS namespace
          ON namespace.oid = relation.relnamespace
        WHERE relation.oid = pg_catalog.to_regclass('alembic_version')
          AND relation.relkind IN ('r', 'p')
        """
    ).scalar_one_or_none()

    if schema is None:
        return False

    quoted_schema = connection.dialect.identifier_preparer.quote(schema)
    connection.exec_driver_sql(
        f"ALTER TABLE {quoted_schema}.alembic_version "
        f"ALTER COLUMN version_num TYPE VARCHAR({ALEMBIC_VERSION_NUM_LENGTH})"
    )
    connection.commit()

    actual_length = connection.exec_driver_sql(
        """
        SELECT character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = 'alembic_version'
          AND column_name = 'version_num'
        """,
        (schema,),
    ).scalar_one_or_none()

    if actual_length is None or actual_length < ALEMBIC_VERSION_NUM_LENGTH:
        raise RuntimeError(
            "Could not widen Alembic version column "
            f"{schema}.alembic_version.version_num to "
            f"VARCHAR({ALEMBIC_VERSION_NUM_LENGTH}); found {actual_length!r}."
        )

    return True


RAW_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rwa-intelligence.db")
DATABASE_URL = normalise_database_url(RAW_DATABASE_URL)
APP_ENV = os.getenv("APP_ENV", "development")
if APP_ENV == "production" and not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise RuntimeError("Production requires a PostgreSQL DATABASE_URL using the psycopg driver.")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=_connect_args,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
