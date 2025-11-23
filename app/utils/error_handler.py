"""
Centralized error handling and logging utilities.

This module provides:
- Custom exception classes for different error types
- Centralized error logging with context
- Decorators for consistent error handling
"""
import logging
from functools import wraps
from typing import Callable, Any
from flask import current_app, flash, redirect, url_for
from app.extensions import db

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass


class NotFoundError(Exception):
    """Custom exception for resource not found errors."""
    pass


def log_error(error: Exception, context: str = "", level: str = "error") -> None:
    """
    Centralized error logging with context.
    
    Args:
        error: The exception that occurred
        context: Additional context about where/why the error occurred
        level: Logging level ('error', 'warning', 'info', 'debug')
    """
    log_method = getattr(logger, level, logger.error)
    log_method(
        f"{context}: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={'context': context, 'error_type': type(error).__name__}
    )


def handle_db_errors(f: Callable) -> Callable:
    """
    Decorator to handle database errors consistently.
    
    Automatically rolls back database transactions on error
    and logs the error with context.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            log_error(e, f"Database error in {f.__name__}")
            flash('An error occurred while processing your request. Please try again.', 'danger')
            # Try to redirect to a safe page, fallback to index
            try:
                return redirect(url_for('main.index'))
            except Exception:
                return redirect('/')
    return decorated_function


def handle_validation_errors(f: Callable) -> Callable:
    """
    Decorator to handle validation errors consistently.
    
    Catches ValidationError exceptions and displays user-friendly messages.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            log_error(e, f"Validation error in {f.__name__}", level="warning")
            flash(str(e), 'warning')
            # Return None to let the route handle the redirect
            return None
        except Exception as e:
            log_error(e, f"Unexpected error in {f.__name__}")
            flash('An unexpected error occurred. Please try again.', 'danger')
            return None
    return decorated_function

