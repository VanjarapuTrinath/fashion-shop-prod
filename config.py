import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-fallback-secret-key-for-local-testing-only')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True' # Controlled by env var, default False

    # Database configuration for MySQL
    # THIS MUST POINT TO YOUR PRODUCTION MYSQL DATABASE
    # It's best to set DATABASE_URL as an environment variable on your server
    # Example: mysql+pymysql://myuser:mypassword@my.remote.mysql.host:3306/mydbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://flask_user:Trinath%403@127.0.0.1/fashion_shop_db'
    # IMPORTANT: In production, the '127.0.0.1' or 'localhost' above
    # should be replaced by the actual hostname/IP of your MySQL server if it's separate.
    # If your MySQL is on the same VM, 127.0.0.1 is fine.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "host": os.environ.get('DB_HOST', '127.0.0.1'),
            "port": int(os.environ.get('DB_PORT', 3306)),
            "user": os.environ.get('DB_USER', 'flask_user'),
            "password": os.environ.get('DB_PASSWORD'), # Plain password here, will be securely loaded
            "database": os.environ.get('DB_NAME'),
        }
    }

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
