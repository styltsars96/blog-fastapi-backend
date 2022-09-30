"""create uuid extension

Revision ID: cb1409f3e7c2
Revises: 
Create Date: 2022-09-29 00:12:29.425979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cb1409f3e7c2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute('create extension "uuid-ossp"')


def downgrade():
    conn = op.get_bind()
    conn.execute('drop extension "uuid-ossp"')
