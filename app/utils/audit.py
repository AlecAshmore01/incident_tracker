"""
Centralized audit logging utility.

This module provides a single function for creating audit logs
consistently across the application, eliminating code duplication.
"""
from typing import Optional
from app.extensions import db
from app.models.audit import AuditLog
from flask_login import current_user
from app.utils.error_handler import log_error


def create_audit_log(
    action: str,
    target_type: str,
    target_id: int,
    user_id: Optional[int] = None
) -> Optional[AuditLog]:
    """
    Create an audit log entry for a user action.
    
    This function centralizes audit log creation to eliminate duplication
    and ensure consistent logging across the application.
    
    Args:
        action: The action performed (e.g., 'create', 'update', 'delete')
        target_type: The type of entity affected (e.g., 'Incident', 'Category')
        target_id: The ID of the affected entity
        user_id: Optional user ID (defaults to current_user.id)
    
    Returns:
        The created AuditLog object, or None if creation failed
    
    Raises:
        DatabaseError: If the audit log cannot be created
    """
    try:
        # Use provided user_id or fall back to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                log_error(
                    Exception("No authenticated user for audit log"),
                    "create_audit_log",
                    level="warning"
                )
                return None
            user_id = current_user.id
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id
        )
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        db.session.rollback()
        # Log error but don't fail the main operation
        log_error(e, f"Failed to create audit log: {action} on {target_type} {target_id}")
        # Return None instead of raising to avoid breaking the main operation
        return None

