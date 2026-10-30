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
            "effective_at", "source", "evidence_ref", "notes", "is_verified",
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
