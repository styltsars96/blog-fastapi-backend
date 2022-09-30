"""post content update

Revision ID: 35f0586efbef
Revises: f3a20d565c32
Create Date: 2022-09-30 00:06:38.550845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "35f0586efbef"
down_revision = "f3a20d565c32"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "post", sa.Column("post_content", sa.String(length=1000), nullable=True)
    )
    op.drop_column("post", "content")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "post", sa.Column("content", sa.TEXT(), autoincrement=False, nullable=True)
    )
    op.drop_column("post", "post_content")
    # ### end Alembic commands ###
