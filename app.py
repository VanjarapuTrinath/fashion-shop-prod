# fashion-shop/app.py

from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

# Create the Flask application instance
app = Flask(__name__)
# Load configuration from Config class
app.config.from_object(Config)

# Initialize CSRFProtect with the Flask app
csrf = CSRFProtect(app)

# Initialize SQLAlchemy with the Flask app
# REMOVED: engine_options argument
db.init_app(app) # Should be just this line now

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # The route name for the login page

# This function tells Flask-Login how to load a user from their ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make datetime.utcnow available in Jinja2 templates for the footer
app.jinja_env.globals.update(now=datetime.utcnow)

# Import routes AFTER app and db are initialized to avoid circular imports
from routes import *

# This block runs the application when you execute app.py
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # This will create tables in your MySQL database

        # Optional: Add some initial categories if they don't exist
        from models import Category
        if not Category.query.first():
            print("Adding initial categories...")
            db.session.add(Category(name='Men\'s Wear', slug='mens-wear'))
            db.session.add(Category(name='Women\'s Wear', slug='womens-wear'))
            db.session.add(Category(name='Accessories', slug='accessories'))
            db.session.add(Category(name='Footwear', slug='footwear'))
            db.session.commit()
            print("Categories added.")

        # Check if an admin user already exists before creating one
        admin_email = 'Thiru@gmail.com'
        if not User.query.filter_by(email=admin_email).first():
            print(f"Creating admin user with email {admin_email}...")
            admin_user = User(username='admin', email=admin_email, is_admin=True)
            admin_user.set_password('741852963') # IMPORTANT: Change this to a strong password!
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print(f"Admin user with email {admin_email} already exists. Skipping creation.")

    app.run(debug=True) # Run the app in debug mode (auto-reloads on code changes)