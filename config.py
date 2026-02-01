import os
import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-unsecure-key-change-it')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-unsecure-key-change-it')
    # JWT Cookie Setup
    JWT_TOKEN_LOCATION = ['cookies']
    
    # Secure cookies in production
    ENV = os.environ.get('FLASK_ENV', 'production')
    JWT_COOKIE_SECURE = True if ENV == 'production' else False
    
    JWT_COOKIE_CSRF_PROTECT = True 
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=15)
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

