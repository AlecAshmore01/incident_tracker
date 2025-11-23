"""
WSGI entry point for production deployment.
This file is used by gunicorn to serve the application.
"""
import os
from app import create_app

# Use production config if FLASK_ENV is set to production, otherwise dev
config_name = os.environ.get('FLASK_ENV', 'production')  # Default to production for deployment
app = create_app(config_name)

if __name__ == '__main__':
    app.run()

