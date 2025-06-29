"""Add closed_at to Incident

Revision ID: 994679cd5277
Revises: 7b9a350afb10
Create Date: 2025-06-17 17:11:41.268932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '994679cd5277'
down_revision = '7b9a350afb10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('incidents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('closed_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('incidents', schema=None) as batch_op:
        batch_op.drop_column('closed_at')

    # ### end Alembic commands ###
