from collections.abc import Generator
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker


ALEMBIC_VERSION_NUM_LENGTH = 128


def normalise_database_url(value: str) -> str:
    """Use the explicitly installed psycopg v3 driver for PostgreSQL URLs."""
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value.removeprefix("postgres://")
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value.removeprefix("postgresql://")
    return value


def ensure_alembic_version_column_length(connection) -> bool:
    """Widen Alembic's existing revision column before migrations run.

    Use PostgreSQL's own search_path resolution, matching Alembic's unqualified
    UPDATE of alembic_version. Do not rely on SQLAlchemy reflection to decide
    whether the table exists: reflection can inspect a different visible
    schema when a database has a non-default search_path.
    """
    if connection.dialect.name != "postgresql":
        return False

    connection.exec_driver_sql(
        "ALTER TABLE IF EXISTS alembic_version "
        f"ALTER COLUMN version_num TYPE VARCHAR({ALEMBIC_VERSION_NUM_LENGTH})"
    )
    connection.commit()

    result = connection.exec_driver_sql(
        """
        SELECT character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'alembic_version'
          AND column_name = 'version_num'
          AND table_schema = ANY(current_schemas(false))
        ORDER BY array_position(current_schemas(false), table_schema)
        LIMIT 1
        """
    ).scalar_one_or_none()

    # No row means this is a fresh database; Alembic will create the table
    # using version_num_length=ALEMBIC_VERSION_NUM_LENGTH.
    if result is not None and result < ALEMBIC_VERSION_NUM_LENGTH:
        raise RuntimeError(
            "Could not widen alembic_version.version_num: "
            f"expected VARCHAR({ALEMBIC_VERSION_NUM_LENGTH}), found VARCHAR({result})."
        )
    return result is not None


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
