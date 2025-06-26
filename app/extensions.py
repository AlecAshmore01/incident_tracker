from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_whooshee import Whooshee
from flask import Flask

db = SQLAlchemy()
migrate = Migrate()
login_mgr = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)
bcrypt = Bcrypt()
mail = Mail()
whooshee = Whooshee()

CSP = {
    'default-src': ["'self'"],
    'style-src':   ["'self'", 'https://cdn.jsdelivr.net', 'https://fonts.googleapis.com'],
    'font-src':    ["'self'", 'https://fonts.gstatic.com'],
    'script-src':  ["'self'", 'https://cdn.jsdelivr.net'],
    'img-src':     ["'self'", 'data:'],
}


def init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    login_mgr.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    whooshee.init_app(app)
    talisman.init_app(
        app,
        content_security_policy=CSP,
        content_security_policy_nonce_in=['script-src']
    )

    # Redirect unauthorized users to login page
    login_mgr.login_view = 'auth.login'
