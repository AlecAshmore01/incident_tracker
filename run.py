from app import create_app
import os

# Use production config if FLASK_ENV is set to production, otherwise dev
config_name = os.environ.get('FLASK_ENV', 'dev')
if config_name == 'production':
    app = create_app('production')
else:
    app = create_app('dev')

if __name__ == '__main__':
    app.run()
