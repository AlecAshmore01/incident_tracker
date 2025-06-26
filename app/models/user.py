from typing import Any, Optional
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from app.extensions import db, login_mgr, bcrypt
from flask import current_app
import pyotp


class User(UserMixin, db.Model):  # type: ignore
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)
    role: str = db.Column(db.String(20), default='regular', nullable=False)

    # Lockout fields
    failed_logins: int = db.Column(db.Integer, default=0, nullable=False)
    lock_until: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    # TOTP 2FA secret (base32)
    otp_secret: Optional[str] = db.Column(db.String(32), nullable=True)

    # Relationships
    incidents = db.relationship('Incident', backref='creator', lazy='dynamic')

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_locked(self) -> bool:
        """Return True if the account is currently locked."""
        if self.lock_until and datetime.utcnow() < self.lock_until:
            return True
        return False

    def register_failed_login(self, max_attempts: int = 5, lock_minutes: int = 15) -> None:
        """
        Increment failure count; lock account if threshold reached.
        Resets failed_logins and sets lock_until when exceeded.
        """
        self.failed_logins += 1
        if self.failed_logins >= max_attempts:
            self.lock_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            self.failed_logins = 0
        db.session.commit()

    def reset_failed_logins(self) -> None:
        """Clear failure count and unlock account after a successful login."""
        self.failed_logins = 0
        self.lock_until = None
        db.session.commit()

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'

    def get_totp_uri(self) -> str:
        """Return provisioning URL for authenticator apps."""
        if self.otp_secret is None:
            raise ValueError("otp_secret is not set for this user.")
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.email,
            issuer_name="IncidentTracker"
        )

    def generate_otp_secret(self) -> None:
        """Create a new base32 secret for this user."""
        self.otp_secret = pyotp.random_base32()
        db.session.commit()

    def get_reset_password_token(self, expires_sec: int = 600) -> str:
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt='password-reset-salt')

    @staticmethod
    def verify_reset_password_token(token: str) -> Optional["User"]:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=600)
        except Exception:
            return None
        return db.session.get(User, user_id)


@login_mgr.user_loader
def load_user(user_id: Any) -> Optional[User]:
    return db.session.get(User, int(user_id))
