from datetime import datetime
from app.extensions import db, whooshee
from typing import Optional
from sqlalchemy.orm import validates
from app.utils.error_handler import ValidationError


@whooshee.register_model('title', 'description')
class Incident(db.Model):  # type: ignore
    __tablename__ = 'incidents'
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(140), nullable=False)
    description: str = db.Column(db.Text, nullable=False)
    status: str = db.Column(db.String(20), default='Open', nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    closed_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id: int = db.Column(db.Integer, db.ForeignKey('incident_categories.id'), nullable=False, index=True)

    def __repr__(self) -> str:
        return f'<Incident {self.title} by User {self.user_id}>'

    @validates('title')
    def validate_title(self, key: str, value: str) -> str:
        """Validate incident title."""
        if not value or not value.strip():
            raise ValidationError("Title cannot be empty")
        value = value.strip()
        if len(value) < 3:
            raise ValidationError("Title must be at least 3 characters long")
        if len(value) > 140:
            raise ValidationError("Title cannot exceed 140 characters")
        # Check for HTML tags
        if '<' in value or '>' in value:
            raise ValidationError("Title cannot contain HTML tags")
        return value

    @validates('description')
    def validate_description(self, key: str, value: str) -> str:
        """Validate incident description."""
        if not value or not value.strip():
            raise ValidationError("Description cannot be empty")
        if len(value.strip()) < 10:
            raise ValidationError("Description must be at least 10 characters long")
        return value

    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        """Validate incident status."""
        allowed_statuses = ['Open', 'In Progress', 'Closed']
        if value not in allowed_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value
