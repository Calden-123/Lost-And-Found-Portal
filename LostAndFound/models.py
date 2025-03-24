# LostAndFound/models.py
from .db import db  # Correct import of db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # This column stores the hashed password
    phone = db.Column(db.String(15), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='user', lazy=True)

    # Set the password and hash it
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check the password
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Item Table
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="Lost")  # Lost or Found
    location = db.Column(db.String(100), nullable=False)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

     