"""Add lockout fields to User

Revision ID: cca0e8aacbe1
Revises: 0c547c870a1b
Create Date: 2025-06-17 12:48:05.749303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cca0e8aacbe1'
down_revision = '0c547c870a1b'
branch_labels = None
depends_on = None


def upgrade():
    # Conditional column addition to avoid duplicates
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = [c['name'] for c in insp.get_columns('users')]

    # Add 'failed_logins' if missing
    if 'failed_logins' not in existing_cols:
        op.add_column(
            'users',
            sa.Column('failed_logins', sa.Integer(), nullable=True)
        )
        # Backfill default
        op.execute("UPDATE users SET failed_logins = 0")
        # Make non-nullable
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column(
                'failed_logins', existing_type=sa.Integer(), nullable=False
            )

    # Add 'lock_until' if missing
    if 'lock_until' not in existing_cols:
        op.add_column(
            'users',
            sa.Column('lock_until', sa.DateTime(), nullable=True)
        )
# ### end Alembic commands ###
