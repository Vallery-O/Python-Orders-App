import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///orderapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv('CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    AFRICASTALKING_USERNAME = os.getenv('AFRICASTALKING_USERNAME' )
    AFRICASTALKING_API_KEY = os.getenv('AFRICASTALKING_API_KEY')