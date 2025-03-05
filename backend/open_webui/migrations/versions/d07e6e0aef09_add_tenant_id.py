"""add tenant_id

Revision ID: d07e6e0aef09
Revises: 3781e22d8b01
Create Date: 2025-03-05 16:19:10.106136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'd07e6e0aef09'
down_revision: Union[str, None] = '3781e22d8b01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def get_object_tables(conn):
    return [table for table in sqlalchemy.inspect(conn).get_table_names() if table not in ("migratehistory", "alembic_version")]


def upgrade() -> None:
    conn = op.get_bind()
    for table in get_object_tables(conn):
        op.add_column(table, sa.Column('tenant_id', sa.TEXT(), server_default=sa.text("COALESCE(current_setting('app.tenant_id'::text, true), 'notenant'::text)"), autoincrement=False, nullable=False))
        conn.execute(sqlalchemy.text(f"""alter table "{table}" enable row level security"""))
        conn.execute(sqlalchemy.text(f"""alter table "{table}" force row level security"""))
        conn.execute(sqlalchemy.text(f"""create policy "{table}_tenant_isolation" on "{table}" using (tenant_id = current_setting('app.tenant_id'))"""))

def downgrade():
    conn = op.get_bind()
    for table in get_object_tables(conn):
        conn.execute(sqlalchemy.text(f"""alter table "{table}" drop column tenant_id cascade""")) # run as a raw query so the drop can cascade to the policy
        conn.execute(sqlalchemy.text(f"""alter table "{table}" disable row level security"""))
