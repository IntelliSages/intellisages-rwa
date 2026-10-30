from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from fastapi.testclient import TestClient

from app import main
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



def test_alembic_version_column_widening_alters_and_verifies_postgres():
    class Result:
        def scalar_one_or_none(self):
            return 128

    class PostgreSQLConnection:
        class Dialect:
            name = "postgresql"

        dialect = Dialect()

        def __init__(self):
            self.statements = []
            self.committed = False

        def exec_driver_sql(self, statement):
            self.statements.append(statement)
            return Result()

        def commit(self):
            self.committed = True

    connection = PostgreSQLConnection()
    assert ensure_alembic_version_column_length(connection) is True
    assert "ALTER TABLE IF EXISTS alembic_version" in connection.statements[0]
    assert "VARCHAR(128)" in connection.statements[0]
    assert connection.committed is True


def test_alembic_version_column_widening_fails_if_postgres_width_is_still_short():
    class Result:
        def scalar_one_or_none(self):
            return 32

    class PostgreSQLConnection:
        class Dialect:
            name = "postgresql"

        dialect = Dialect()

        def exec_driver_sql(self, statement):
            return Result()

        def commit(self):
            pass

    import pytest

    with pytest.raises(RuntimeError, match="expected VARCHAR\\(128\\)"):
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
