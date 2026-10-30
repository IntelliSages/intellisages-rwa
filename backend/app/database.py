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
    """Expand an existing PostgreSQL Alembic revision column before migrations.

    Alembic defaults this column to VARCHAR(32). The repository has revision
    identifiers longer than 32 characters, so existing databases need a
    one-time widening before Alembic records the next revision.
    """
    if connection.dialect.name != "postgresql":
        return False

    inspector = inspect(connection)
    if "alembic_version" not in inspector.get_table_names():
        return False

    columns = inspector.get_columns("alembic_version")
    version_column = next((column for column in columns if column["name"] == "version_num"), None)
    if version_column is None:
        return False

    current_length = getattr(version_column["type"], "length", None)
    if current_length is not None and current_length >= ALEMBIC_VERSION_NUM_LENGTH:
        return False

    connection.exec_driver_sql(
        f"ALTER TABLE alembic_version ALTER COLUMN version_num "
        f"TYPE VARCHAR({ALEMBIC_VERSION_NUM_LENGTH})"
    )
    connection.commit()
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
