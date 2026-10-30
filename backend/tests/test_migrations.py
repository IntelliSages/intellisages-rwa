from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def test_effective_alias_migration_preserves_legacy_alias_without_inventing_dates(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy-alias.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")

    command.upgrade(config, "0002_supply_classification")
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO provider_aliases
                    (id, provider, namespace, external_id, entity_type, entity_id, evidence_ref, is_verified)
                VALUES
                    ('legacy-alias', 'coingecko', 'coin', 'legacy-nvda', 'underlying',
                     'legacy-underlying', 'legacy-evidence', 0)
                """
            )
        )
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT effective_from, effective_to FROM provider_aliases WHERE id = 'legacy-alias'"
            )
        ).one()
        assert row.effective_from is None
        assert row.effective_to is None
    engine.dispose()

    command.downgrade(config, "base")

def test_downgrade_refuses_to_collapse_multiple_alias_periods(tmp_path, monkeypatch):
    database_path = tmp_path / "alias-history.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")

    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO provider_aliases
                    (id, provider, namespace, external_id, effective_from, effective_to,
                     entity_type, entity_id, evidence_ref, is_verified)
                VALUES
                    ('alias-period-1', 'coingecko', 'symbol', 'NVDA', '2026-01-01', '2026-06-01',
                     'underlying', 'underlying-a', 'evidence-a', 0),
                    ('alias-period-2', 'coingecko', 'symbol', 'NVDA', '2026-06-01', NULL,
                     'underlying', 'underlying-b', 'evidence-b', 0)
                """
            )
        )
    engine.dispose()

    import pytest
    with pytest.raises(RuntimeError, match="multiple periods"):
        command.downgrade(config, "0002_supply_classification")

    engine = create_engine(database_url)
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM provider_aliases WHERE external_id = 'NVDA'")
        ).scalar_one()
        assert count == 2
    engine.dispose()



def test_perpetual_contract_migration_table_upgrades_and_downgrades_cleanly(tmp_path, monkeypatch):
    database_path = tmp_path / "perpetual-migrations.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")

    command.upgrade(config, "0003_effective_provider_aliases")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        tables_before = {
            row[0] for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).all()
        }
        assert "perpetual_contract_migrations" not in tables_before
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        columns = {
            row[1] for row in connection.execute(
                text("PRAGMA table_info(perpetual_contract_migrations)")
            ).all()
        }
        assert {
            "id", "predecessor_contract_id", "successor_contract_id", "event_type",
            "effective_at", "previous_native_market_id", "new_native_market_id",
            "previous_native_symbol", "new_native_symbol", "source", "evidence_ref",
            "notes", "is_verified",
        }.issubset(columns)
    engine.dispose()

    command.downgrade(config, "0003_effective_provider_aliases")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        tables_after = {
            row[0] for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).all()
        }
        assert "perpetual_contract_migrations" not in tables_after
    engine.dispose()



def test_provider_ingestion_run_migration_upgrades_and_downgrades(tmp_path, monkeypatch):
    database_path = tmp_path / "provider-ingestion.db"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "0005_registry_import_reconciliation")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        before = {row[0] for row in connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")).all()}
        assert "provider_ingestion_runs" not in before
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        columns = {row[1] for row in connection.execute(
            text("PRAGMA table_info(provider_ingestion_runs)")).all()}
        assert {"id", "provider", "dataset", "source_version", "started_by", "status",
                "manifest_sha256", "coverage_json", "staged_batch_ids_json",
                "created_at", "updated_at", "completed_at"}.issubset(columns)
    engine.dispose()

    command.downgrade(config, "0005_registry_import_reconciliation")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        after = {row[0] for row in connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")).all()}
        assert "provider_ingestion_runs" not in after
    engine.dispose()



def test_pre_migration_inspection_transaction_is_closed_before_upgrade(tmp_path):
    from app.database import commit_pre_migration_transaction

    database_path = tmp_path / "pre-migration-transaction.db"
    database_url = f"sqlite:///{database_path}"
    engine = create_engine(database_url)

    # A diagnostic SELECT autobegins a transaction in SQLAlchemy 2.x.
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        assert connection.in_transaction()

        commit_pre_migration_transaction(connection)
        assert not connection.in_transaction()

        # Alembic can now own and commit its migration transaction.
        with connection.begin():
            connection.execute(
                text("CREATE TABLE migration_transaction_probe (id INTEGER PRIMARY KEY)")
            )

    # Closing the connection must not roll back the migration's DDL.
    with engine.connect() as connection:
        table = connection.execute(
            text(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'migration_transaction_probe'
                """
            )
        ).scalar_one_or_none()
        assert table == "migration_transaction_probe"

    engine.dispose()
