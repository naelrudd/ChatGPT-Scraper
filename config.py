import os

class Config:
    # Konfigurasi Dasar
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ganti-dengan-secret-key-yang-aman'
    
    # Konfigurasi Database
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'chatgpt_scraper'
    SQLALCHEMY_DATABASE_URI = f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi Aplikasi
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    
    # Konfigurasi Keamanan
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True 