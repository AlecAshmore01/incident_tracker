import os
from app import create_app

# Use production config if FLASK_ENV is set to production, otherwise dev
# This ensures app is always available at module level for gunicorn
config_name = os.environ.get('FLASK_ENV', 'dev')
if config_name == 'production':
    app = create_app('production')
else:
    app = create_app('dev')

# Make app available for gunicorn (gunicorn run:app looks for 'app' variable)
if __name__ == '__main__':
    app.run(debug=(config_name != 'production'))
