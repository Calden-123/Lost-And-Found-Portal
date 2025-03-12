from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config  # Import the Config class

# Initialize db instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set configuration from Config class
    app.config.from_object(Config)  # Load configuration from the Config class

    # Initialize the app with the db
    db.init_app(app)

    return app
