"""Add performance indexes

Revision ID: add_perf_indexes
Revises: cca0e8aacbe1
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_perf_indexes'
down_revision = '994679cd5277'
branch_labels = None
depends_on = None


def upgrade():
    # Indexes for incidents table
    op.create_index('ix_incidents_user_id', 'incidents', ['user_id'], unique=False)
    op.create_index('ix_incidents_category_id', 'incidents', ['category_id'], unique=False)
    op.create_index('ix_incidents_status', 'incidents', ['status'], unique=False)
    # timestamp already has index from initial schema, but ensure it exists
    try:
        op.create_index('ix_incidents_timestamp', 'incidents', ['timestamp'], unique=False)
    except Exception:
        pass  # Index may already exist
    
    # Indexes for users table
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    
    # Indexes for categories table
    op.create_index('ix_incident_categories_name', 'incident_categories', ['name'], unique=False)
    
    # Indexes for audit_logs table
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_audit_logs_target_type', 'audit_logs', ['target_type'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('ix_audit_logs_target_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_incident_categories_name', table_name='incident_categories')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    try:
        op.drop_index('ix_incidents_timestamp', table_name='incidents')
    except Exception:
        pass
    op.drop_index('ix_incidents_status', table_name='incidents')
    op.drop_index('ix_incidents_category_id', table_name='incidents')
    op.drop_index('ix_incidents_user_id', table_name='incidents')

