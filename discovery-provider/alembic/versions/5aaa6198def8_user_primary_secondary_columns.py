"""user primary secondary columns

Revision ID: 5aaa6198def8
Revises: 6d1b38f242fe
Create Date: 2020-12-22 13:00:09.925084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5aaa6198def8'
down_revision = 'a88a8ce41f7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('primaryID', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('secondaryIDs', sa.ARRAY(sa.Integer()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'primaryID')
    op.drop_column('users', 'secondaryIDs')
    # ### end Alembic commands ###
