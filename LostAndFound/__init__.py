from flask import Flask
from .config import Config
from .db import db  



def create_app():
    app = Flask(__name__)

    # Set configuration from Config class
    app.config.from_object(Config)  # Load configuration from the Config class

    # Initialize the app with the db
    db.init_app(app)

    return app
