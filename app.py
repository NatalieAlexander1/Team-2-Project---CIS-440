import os
from flask import Flask
from extensions import db, jwt, cors
from gevent import monkey

# Patch for gevent compatibility
monkey.patch_all()

# Try to import the Config class from config.py (if it exists)
try:
    from config import Config
    config_available = True
except ImportError:
    print("config.py not found. Falling back to environment variables.")
    config_available = False


def create_app():
    app = Flask(__name__)

    # If config.py is available, use it. Otherwise, rely on environment variables.
    if config_available:
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_recycle': 28000,  # Prevent connections from timing out
            'pool_pre_ping': True   # Check connections before using them
        }
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)  # Default to False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Provide a default or ensure it's set in production

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints for routing
    from routes import routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


# Create the app instance
app = create_app()
