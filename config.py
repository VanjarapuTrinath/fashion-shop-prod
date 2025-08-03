# fashion-shop/config.py

import os

# Get the directory where this config.py file is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # A secret key is used for session management and security.
    # ALWAYS change this to a long, random string in a real application!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-you-should-change-in-production-seriously-12345'

    # Database configuration for MySQL
    # Keep the URI as it was, with URL-encoded password if needed
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://flask_user:Trinath%403@127.0.0.1/fashion_shop_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable tracking modifications to save memory

    # ADDED: Explicit engine options for pymysql's connect_args
    # This is where we pass the host, port, user, password, and database explicitly
    # This helps bypass any parsing issues with special characters in the URI string itself.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "host": "127.0.0.1", # Your MySQL host
            "port": 3306,        # Default MySQL port
            "user": "root", # Your MySQL username
            "password": "Trinath@3", # Your ACTUAL password (no URL encoding needed here!)
            "database": "fashion_shop_db", # Your database name
        }
    }

    # Where uploaded product images will be stored
    UPLOAD_FOLDER = os.path.join(basedir, 'static/images/products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}