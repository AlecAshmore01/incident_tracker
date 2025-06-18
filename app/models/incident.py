from datetime import datetime
from app.extensions import db, whooshee
from typing import Optional


@whooshee.register_model('title', 'description')
class Incident(db.Model):
    __tablename__ = 'incidents'
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(140), nullable=False)
    description: str = db.Column(db.Text, nullable=False)
    status: str = db.Column(db.String(20), default='Open', nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    closed_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id: int = db.Column(db.Integer, db.ForeignKey('incident_categories.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<Incident {self.title} by User {self.user_id}>'
