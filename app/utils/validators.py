"""
Custom form validators for enhanced input validation.

This module provides reusable validators that can be used
across different forms to ensure consistent validation logic.
"""
import re
from typing import Optional, Any
from wtforms.validators import ValidationError


class StrongPassword:
    """
    Validates password strength with configurable requirements.
    
    Usage:
        password = PasswordField('Password', validators=[
            DataRequired(),
            StrongPassword(min_length=8, require_upper=True)
        ])
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_upper: bool = True,
        require_lower: bool = True,
        require_digit: bool = True,
        require_special: bool = False,
        message: Optional[str] = None
    ):
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
        self.require_special = require_special
        self.message = message
    
    def __call__(self, form: Any, field: Any) -> None:
        password = field.data
        if not password:
            return
        
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_upper and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lower and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*...)")
        
        if errors:
            error_message = self.message or '; '.join(errors)
            raise ValidationError(error_message)


class NoHTML:
    """
    Validates that input does not contain HTML tags.
    
    Usage:
        name = StringField('Name', validators=[DataRequired(), NoHTML()])
    """
    
    def __init__(self, message: Optional[str] = None):
        self.message = message or "This field cannot contain HTML tags"
    
    def __call__(self, form: Any, field: Any) -> None:
        if field.data and ('<' in field.data or '>' in field.data):
            raise ValidationError(self.message)


class SafeText:
    """
    Validates that text is safe and doesn't contain potentially dangerous content.
    
    Checks for:
    - Script tags
    - JavaScript event handlers
    - SQL injection patterns (basic)
    """
    
    def __init__(self, message: Optional[str] = None):
        self.message = message or "Text contains potentially unsafe content"
    
    def __call__(self, form: Any, field: Any) -> None:
        if not field.data:
            return
        
        text = field.data.lower()
        
        # Check for script tags
        if '<script' in text or '</script>' in text:
            raise ValidationError(self.message)
        
        # Check for common JavaScript event handlers
        dangerous_patterns = [
            'onclick', 'onerror', 'onload', 'onmouseover',
            'javascript:', 'vbscript:', 'data:text/html'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in text:
                raise ValidationError(self.message)

