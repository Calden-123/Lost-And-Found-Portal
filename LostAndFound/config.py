import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))  # Get the absolute path of the current directory
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))  # Use os.urandom to generate a secure random key if not set

    # Change the path to point outside the LostAndFound folder
    database_path = os.path.abspath(os.path.join(basedir, '..', 'instance', 'lost_and_found.db'))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + database_path)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Print the absolute path of the database for debugging
    print("Database Path:", database_path)
