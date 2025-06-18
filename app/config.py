import os
import logging
from logging.handlers import TimedRotatingFileHandler

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    MAIL_SERVER = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS',  'True') in ['True', 'true', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL',  'False') in ['True', 'true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')    # e.g. your Gmail or Mailtrap user
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')    # app-password or Mailtrap pass
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_SUPPRESS_SEND = False  # ensure we actually _try_ to send
    WHOOSH_BASE = os.path.join(basedir, 'whoosh_index')


class DevConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProdConfig(Config):
    DEBUG = False

    @staticmethod
    def init_app(app):
        handler = TimedRotatingFileHandler(
            'logs/app.log', when='D', interval=1, backupCount=7
        )
        handler.setLevel(logging.INFO)
        fmt = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        handler.setFormatter(fmt)
        app.logger.addHandler(handler)
