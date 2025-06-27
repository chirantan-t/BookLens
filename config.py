# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_and_random_string_that_you_should_change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Other configurations can go here