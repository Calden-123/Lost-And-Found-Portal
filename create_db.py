from LostAndFound import create_app
from LostAndFound.db import db  # Correct import of db
from LostAndFound.models import User, Item


app = create_app()

with app.app_context():
    db.create_all()  # This creates the tables based on the models
    print("Tables created successfully!")
