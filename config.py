import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///orderapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv('CLIENT_ID', '44487251457-9ncb9j64e73neq7e0sk6nj26fm3mcbau.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.getenv('CLIENT_SECRET', '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')
    AFRICASTALKING_USERNAME = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
    AFRICASTALKING_API_KEY = os.getenv('AFRICASTALKING_API_KEY', 'atsk_0e353ed97ba9a626028f4af5a7e4acdfa2b895381e3c9d6c61c3d326ac5133155cb54675')