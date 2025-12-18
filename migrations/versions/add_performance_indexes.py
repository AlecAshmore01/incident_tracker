"""Add performance indexes

Revision ID: add_perf_indexes
Revises: cca0e8aacbe1
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'add_perf_indexes'
down_revision = '994679cd5277'
branch_labels = None
depends_on = None


def index_exists(table_name: str, index_name: str) -> bool:
    """Check if an index exists on a table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)


def upgrade():
    # Indexes for incidents table
    if not index_exists('incidents', 'ix_incidents_user_id'):
        op.create_index('ix_incidents_user_id', 'incidents', ['user_id'], unique=False)
    if not index_exists('incidents', 'ix_incidents_category_id'):
        op.create_index('ix_incidents_category_id', 'incidents', ['category_id'], unique=False)
    if not index_exists('incidents', 'ix_incidents_status'):
        op.create_index('ix_incidents_status', 'incidents', ['status'], unique=False)
    # timestamp already has index from initial schema, but ensure it exists
    if not index_exists('incidents', 'ix_incidents_timestamp'):
        op.create_index('ix_incidents_timestamp', 'incidents', ['timestamp'], unique=False)
    
    # Indexes for users table
    if not index_exists('users', 'ix_users_username'):
        op.create_index('ix_users_username', 'users', ['username'], unique=False)
    if not index_exists('users', 'ix_users_email'):
        op.create_index('ix_users_email', 'users', ['email'], unique=False)
    if not index_exists('users', 'ix_users_role'):
        op.create_index('ix_users_role', 'users', ['role'], unique=False)
    
    # Indexes for categories table
    if not index_exists('incident_categories', 'ix_incident_categories_name'):
        op.create_index('ix_incident_categories_name', 'incident_categories', ['name'], unique=False)
    
    # Indexes for audit_logs table
    if not index_exists('audit_logs', 'ix_audit_logs_user_id'):
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    if not index_exists('audit_logs', 'ix_audit_logs_timestamp'):
        op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    if not index_exists('audit_logs', 'ix_audit_logs_target_type'):
        op.create_index('ix_audit_logs_target_type', 'audit_logs', ['target_type'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    if index_exists('audit_logs', 'ix_audit_logs_target_type'):
        op.drop_index('ix_audit_logs_target_type', table_name='audit_logs')
    if index_exists('audit_logs', 'ix_audit_logs_timestamp'):
        op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    if index_exists('audit_logs', 'ix_audit_logs_user_id'):
        op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    if index_exists('incident_categories', 'ix_incident_categories_name'):
        op.drop_index('ix_incident_categories_name', table_name='incident_categories')
    if index_exists('users', 'ix_users_role'):
        op.drop_index('ix_users_role', table_name='users')
    if index_exists('users', 'ix_users_email'):
        op.drop_index('ix_users_email', table_name='users')
    if index_exists('users', 'ix_users_username'):
        op.drop_index('ix_users_username', table_name='users')
    if index_exists('incidents', 'ix_incidents_timestamp'):
        op.drop_index('ix_incidents_timestamp', table_name='incidents')
    if index_exists('incidents', 'ix_incidents_status'):
        op.drop_index('ix_incidents_status', table_name='incidents')
    if index_exists('incidents', 'ix_incidents_category_id'):
        op.drop_index('ix_incidents_category_id', table_name='incidents')
    if index_exists('incidents', 'ix_incidents_user_id'):
        op.drop_index('ix_incidents_user_id', table_name='incidents')

