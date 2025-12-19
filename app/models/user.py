from typing import Any, Optional
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from app.extensions import db, login_mgr, bcrypt
from flask import current_app
from sqlalchemy.orm import validates
import pyotp
import re
from app.utils.error_handler import ValidationError


class User(UserMixin, db.Model):  # type: ignore
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(128), nullable=False)
    role: str = db.Column(db.String(20), default='regular', nullable=False, index=True)

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
        # Get lock_until directly from database to avoid stale data
        lock_until = db.session.query(User.lock_until).filter_by(id=self.id).scalar()
        now = datetime.utcnow()
        
        # Clear expired locks
        if lock_until and now >= lock_until:
            db.session.query(User).filter_by(id=self.id).update({'lock_until': None})
            db.session.commit()
            self.lock_until = None
            return False
        
        # Check if currently locked
        if lock_until and now < lock_until:
            # Update self for consistency
            self.lock_until = lock_until
            return True
        return False

    def register_failed_login(self, max_attempts: int = 5, lock_minutes: int = 15) -> None:
        """
        Increment failure count; lock account if threshold reached.
        Resets failed_logins and sets lock_until when exceeded.
        """
        # Get current failed_logins directly from database to avoid stale data
        current_failed = db.session.query(User.failed_logins).filter_by(id=self.id).scalar()
        if current_failed is None:
            current_failed = 0
        
        # Increment
        new_failed = current_failed + 1
        current_app.logger.info(f'Failed login attempt {new_failed}/{max_attempts} for user {self.username}')
        
        # Update database directly
        if new_failed >= max_attempts:
            lock_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            db.session.query(User).filter_by(id=self.id).update({
                'failed_logins': 0,
                'lock_until': lock_until
            })
            current_app.logger.info(f'Account locked for user {self.username} until {lock_until}')
            # Update self
            self.failed_logins = 0
            self.lock_until = lock_until
        else:
            db.session.query(User).filter_by(id=self.id).update({
                'failed_logins': new_failed
            })
            # Update self
            self.failed_logins = new_failed
        
        db.session.commit()

    def reset_failed_logins(self) -> None:
        """Clear failure count and unlock account after a successful login."""
        self.failed_logins = 0
        self.lock_until = None
        db.session.commit()

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'

    @validates('username')
    def validate_username(self, key: str, value: str) -> str:
        """Validate username."""
        if not value or not value.strip():
            raise ValidationError("Username cannot be empty")
        value = value.strip()
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        if len(value) > 64:
            raise ValidationError("Username cannot exceed 64 characters")
        # Check for HTML tags
        if '<' in value or '>' in value:
            raise ValidationError("Username cannot contain HTML tags")
        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError("Username can only contain letters, numbers, underscores, and hyphens")
        return value

    @validates('email')
    def validate_email(self, key: str, value: str) -> str:
        """Validate email address."""
        if not value or not value.strip():
            raise ValidationError("Email cannot be empty")
        value = value.strip().lower()
        if len(value) > 120:
            raise ValidationError("Email cannot exceed 120 characters")
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError("Invalid email format")
        return value

    @validates('role')
    def validate_role(self, key: str, value: str) -> str:
        """Validate user role."""
        allowed_roles = ['regular', 'admin']
        if value not in allowed_roles:
            raise ValidationError(f"Role must be one of: {', '.join(allowed_roles)}")
        return value

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
