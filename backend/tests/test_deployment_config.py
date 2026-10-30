from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from fastapi.testclient import TestClient

from app import main
from alembic.ddl.impl import DefaultImpl
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect
from app.alembic_impl import ExtendedPostgresqlImpl


def test_postgresql_alembic_version_table_uses_extended_column():
    registered_impl = DefaultImpl.get_by_dialect(postgresql_dialect())
    assert registered_impl is ExtendedPostgresqlImpl

    table = registered_impl.version_table_impl(
        version_table="alembic_version",
        version_table_schema=None,
        version_table_pk=True,
    )
    assert table.c.version_num.type.length == ALEMBIC_VERSION_NUM_LENGTH


from app.database import (
    ALEMBIC_VERSION_NUM_LENGTH,
    ensure_alembic_version_column_length,
    normalise_database_url,
)


def test_postgres_urls_use_psycopg_v3():
    assert normalise_database_url("postgres://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )
    assert normalise_database_url("postgresql://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )


def test_non_postgres_url_is_unchanged():
    assert normalise_database_url("sqlite:///./test.db") == "sqlite:///./test.db"


def test_alembic_revision_column_length_supports_long_revision_ids():
    assert ALEMBIC_VERSION_NUM_LENGTH >= len("0004_perpetual_contract_migrations")


def test_alembic_version_column_widening_is_postgres_only():
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        assert ensure_alembic_version_column_length(connection) is False
    engine.dispose()


def test_alembic_version_column_widening_resolves_and_verifies_exact_table():
    class Result:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class IdentifierPreparer:
        def quote(self, identifier):
            return f'"{identifier}"'

    class PostgreSQLConnection:
        class Dialect:
            name = "postgresql"
            identifier_preparer = IdentifierPreparer()

        dialect = Dialect()

        def __init__(self):
            self.statements = []
            self.committed = False

        def exec_driver_sql(self, statement, parameters=None):
            self.statements.append((statement, parameters))
            if len(self.statements) == 1:
                return Result("tenant_schema")
            return Result(128)

        def commit(self):
            self.committed = True

    connection = PostgreSQLConnection()
    assert ensure_alembic_version_column_length(connection) is True
    assert "to_regclass('alembic_version')" in connection.statements[0][0]
    assert 'ALTER TABLE "tenant_schema".alembic_version' in connection.statements[1][0]
    assert connection.statements[2][1] == ("tenant_schema",)
    assert connection.committed is True


def test_alembic_version_column_widening_handles_fresh_database():
    class Result:
        def scalar_one_or_none(self):
            return None

    class PostgreSQLConnection:
        class Dialect:
            name = "postgresql"

        dialect = Dialect()

        def exec_driver_sql(self, statement, parameters=None):
            return Result()

    assert ensure_alembic_version_column_length(PostgreSQLConnection()) is False


def test_alembic_version_column_widening_fails_if_verification_is_short():
    class Result:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class IdentifierPreparer:
        def quote(self, identifier):
            return f'"{identifier}"'

    class PostgreSQLConnection:
        class Dialect:
            name = "postgresql"
            identifier_preparer = IdentifierPreparer()

        dialect = Dialect()

        def __init__(self):
            self.calls = 0

        def exec_driver_sql(self, statement, parameters=None):
            self.calls += 1
            return Result("public" if self.calls == 1 else 32)

        def commit(self):
            pass

    with pytest.raises(RuntimeError, match="public.alembic_version.version_num"):
        ensure_alembic_version_column_length(PostgreSQLConnection())


def test_healthcheck_requires_database_connectivity(monkeypatch):
    engine = create_engine("sqlite://")
    monkeypatch.setattr(main, "engine", engine)
    response = TestClient(main.app).get("/healthz")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "rwa-intelligence-api",
        "database": "connected",
    }
    engine.dispose()


def test_healthcheck_returns_503_when_database_is_unavailable(monkeypatch):
    class UnavailableEngine:
        def connect(self):
            raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(main, "engine", UnavailableEngine())
    response = TestClient(main.app).get("/healthz")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database is unavailable."
