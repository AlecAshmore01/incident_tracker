"""Add otp_secret to User

Revision ID: 99342c40e3b4
Revises: cca0e8aacbe1
Create Date: 2025-06-17 13:26:02.504032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99342c40e3b4'
down_revision = 'cca0e8aacbe1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('otp_secret', sa.String(length=32), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('otp_secret')

    # ### end Alembic commands ###
