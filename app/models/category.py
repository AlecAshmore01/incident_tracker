from typing import Optional
from app.extensions import db
from sqlalchemy.orm import validates
from app.utils.error_handler import ValidationError


class IncidentCategory(db.Model):  # type: ignore
    __tablename__ = 'incident_categories'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description: str = db.Column(db.String(255))
    incidents = db.relationship('Incident', backref='category', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Category {self.name}>'

    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate category name."""
        if not value or not value.strip():
            raise ValidationError("Category name cannot be empty")
        value = value.strip()
        if len(value) < 2:
            raise ValidationError("Category name must be at least 2 characters long")
        if len(value) > 64:
            raise ValidationError("Category name cannot exceed 64 characters")
        # Check for HTML tags
        if '<' in value or '>' in value:
            raise ValidationError("Category name cannot contain HTML tags")
        return value

    @validates('description')
    def validate_description(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate category description."""
        if value is None:
            return None
        value = value.strip() if value else ""
        if value and len(value) > 255:
            raise ValidationError("Description cannot exceed 255 characters")
        return value if value else None
