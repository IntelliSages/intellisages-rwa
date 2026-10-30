from alembic.ddl.postgresql import PostgresqlImpl
from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, String, Table

from app.database import ALEMBIC_VERSION_NUM_LENGTH


class ExtendedPostgresqlImpl(PostgresqlImpl):
    """PostgreSQL Alembic implementation with a wider revision column.

    Alembic 1.16.1's built-in PostgresqlImpl creates alembic_version using
    String(32). Registering this subclass under the same dialect key replaces
    that implementation before MigrationContext builds its version table.
    """

    __dialect__ = "postgresql"

    def version_table_impl(
        self,
        *,
        version_table: str,
        version_table_schema: str | None,
        version_table_pk: bool,
        **kw,
    ) -> Table:
        table = Table(
            version_table,
            MetaData(),
            Column("version_num", String(ALEMBIC_VERSION_NUM_LENGTH), nullable=False),
            schema=version_table_schema,
        )
        if version_table_pk:
            table.append_constraint(
                PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc")
            )
        return table
