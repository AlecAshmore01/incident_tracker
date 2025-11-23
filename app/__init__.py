import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from app.config import DevConfig, ProdConfig
from app.extensions import init_extensions, db
from app.main.routes import main_bp
from app.auth.routes import auth_bp
from app.incidents.routes import incident_bp
from app.categories.routes import category_bp
from app.utils.migration_check import ensure_db_is_up_to_date


def setup_logging(app: Flask) -> None:
    """Configure structured logging for the application."""
    if not app.debug:
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure file handler with rotation
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Configure error handler for errors and above
        error_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'errors.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]\n%(exc_info)s'
        ))
        error_handler.setLevel(logging.ERROR)
        
        # Add handlers to app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')


def create_app(config_name: str = 'dev') -> Flask:
    app = Flask(__name__)
    config = DevConfig if config_name == 'dev' else ProdConfig
    app.config.from_object(config)

    # Configure logging
    setup_logging(app)

    # initialize all extensions (db, migrate, login, csrf, etc.)
    init_extensions(app)

    # ─── expose db on the SQLAlchemy extension so tests can do:
    # client.application.extensions['sqlalchemy'].db.session.commit()
    app.extensions['sqlalchemy'].db = db

    # allow extra per-config init (if any)
    if hasattr(config, 'init_app'):
        config.init_app(app)

    # secure cookies in non-debug
    if not app.debug:
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            REMEMBER_COOKIE_SECURE=True,
        )

    # check migrations at startup (skip during database CLI commands like 'flask db upgrade')
    if not app.debug:
        # Skip migration check if we're running a Flask database CLI command
        # This prevents circular dependency when running 'flask db upgrade'
        # Check if 'db' command appears in the command line arguments
        # This handles both 'flask db upgrade' and 'python -m flask db upgrade' cases
        is_db_cli_command = 'db' in sys.argv
        
        if not is_db_cli_command:
            migrations_path = os.path.join(os.path.dirname(__file__), '..', 'migrations')
            with app.app_context():
                ensure_db_is_up_to_date(db.engine, migrations_path)

    # register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(incident_bp, url_prefix='/incidents')
    app.register_blueprint(category_bp, url_prefix='/categories')

    return app
