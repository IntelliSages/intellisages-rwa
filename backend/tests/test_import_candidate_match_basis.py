from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.models import RegistryImportCandidate

PRODUCT_BASES = [
    "exact_canonical_key",
    "exact_issuer_native_product_id",
    "exact_provider_alias_unverified",
    "exact_provider_alias_verified",
    "symbol_only_do_not_auto_link",
]


def test_match_basis_holds_every_reason_joined_together():
    joined = "|".join(sorted(PRODUCT_BASES))
    assert len(joined) > 80
    column = RegistryImportCandidate.__table__.c.match_basis
    assert column.type.length >= len(joined)


def test_migration_widens_match_basis(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'match-basis.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "0007_coingecko_rwa_market_data")
    engine = create_engine(url)
    cols = inspect(engine).get_columns("registry_import_candidates")
    before = {c["name"]: c for c in cols}
    assert before["match_basis"]["type"].length == 80
    engine.dispose()
    command.upgrade(config, "head")
    engine = create_engine(url)
    cols = inspect(engine).get_columns("registry_import_candidates")
    after = {c["name"]: c for c in cols}
    assert after["match_basis"]["type"].length == 255
    engine.dispose()
    command.downgrade(config, "base")
