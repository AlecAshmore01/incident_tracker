from datetime import datetime
from typing import Optional

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('users.id'))
    action: str = db.Column(db.String(64), nullable=False)
    target_type: str = db.Column(db.String(64), nullable=False)  # e.g. 'Incident'
    target_id: Optional[int] = db.Column(db.Integer, nullable=True)  # e.g. incident.id
    timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationship back to user
    user = db.relationship('User', backref='audit_logs')

    def __repr__(self) -> str:
        return (
            f'<Audit {self.action} by User {self.user_id} on '
            f'{self.target_type} {self.target_id} at {self.timestamp}>'
        )
