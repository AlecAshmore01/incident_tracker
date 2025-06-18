import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db as _db

TEST_DATABASE_URI = "sqlite:///:memory:"

@pytest.fixture(scope='session')
def app():
    """Session‐wide Flask app."""
    os.environ['FLASK_CONFIG'] = 'test'
    cfg = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'WTF_CSRF_ENABLED': False,  # disable CSRF for form tests
        'LOG_TO_FILE': False,
    }
    app = create_app('dev')  # or however you load config
    app.config.update(cfg)

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
