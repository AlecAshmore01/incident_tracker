import os
from flask import Flask
from app.config import DevConfig, ProdConfig
from app.extensions import init_extensions, db
from app.main.routes import main_bp
from app.auth.routes import auth_bp
from app.incidents.routes import incident_bp
from app.categories.routes import category_bp
from app.utils.migration_check import ensure_db_is_up_to_date


def create_app(config_name: str = 'dev') -> Flask:
    app = Flask(__name__)
    config = DevConfig if config_name == 'dev' else ProdConfig
    app.config.from_object(config)

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

    # check migrations at startup
    migrations_path = os.path.join(os.path.dirname(__file__), '..', 'migrations')
    with app.app_context():
        ensure_db_is_up_to_date(db.engine, migrations_path)

    # register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(incident_bp, url_prefix='/incidents')
    app.register_blueprint(category_bp, url_prefix='/categories')

    return app
