from app.extensions import db


class IncidentCategory(db.Model):  # type: ignore
    __tablename__ = 'incident_categories'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(64), unique=True, nullable=False)
    description: str = db.Column(db.String(255))
    incidents = db.relationship('Incident', backref='category', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Category {self.name}>'
