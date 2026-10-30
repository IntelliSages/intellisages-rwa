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


def ensure_alembic_version_column_length(connection) -> bool:
    """Widen every existing Alembic revision column before migrations run.

    PostgreSQL permits multiple schemas to contain an alembic_version table.
    Alembic's unqualified version-table UPDATE resolves through search_path,
    while an ALTER against only one visible table can leave a shadowed table
    at VARCHAR(32). Widen all matching application-schema tables so the
    column Alembic resolves cannot remain undersized.
    """
    if connection.dialect.name != "postgresql":
        return False

    connection.exec_driver_sql(
        """
        DO $alembic_version_width$
        DECLARE
            version_table RECORD;
        BEGIN
            FOR version_table IN
                SELECT table_schema
                FROM information_schema.columns
                WHERE table_name = 'alembic_version'
                  AND column_name = 'version_num'
                  AND table_schema NOT IN ('pg_catalog', 'information_schema')
            LOOP
                EXECUTE format(
                    'ALTER TABLE %I.%I ALTER COLUMN %I TYPE VARCHAR(%s)',
                    version_table.table_schema,
                    'alembic_version',
                    'version_num',
                    128
                );
            END LOOP;
        END
        $alembic_version_width$;
        """
    )
    connection.commit()

    remaining_short_columns = connection.exec_driver_sql(
        """
        SELECT table_schema, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'alembic_version'
          AND column_name = 'version_num'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
          AND (
              character_maximum_length IS NULL
              OR character_maximum_length < %s
          )
        """,
        (ALEMBIC_VERSION_NUM_LENGTH,),
    ).all()

    if remaining_short_columns:
        details = ", ".join(
            f"{schema}.alembic_version.version_num VARCHAR({length})"
            for schema, length in remaining_short_columns
        )
        raise RuntimeError(
            "Could not widen all Alembic version columns to "
            f"VARCHAR({ALEMBIC_VERSION_NUM_LENGTH}): {details}."
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
