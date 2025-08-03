# fashion-shop/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing

db = SQLAlchemy() # Initialize SQLAlchemy here, it will be linked to the app later

# User model: Represents a user of our e-commerce site
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Stores hashed password
    is_admin = db.Column(db.Boolean, default=False) # To distinguish admin users

    # Define relationships: a user can have multiple cart items and orders
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        # Hashes the password before storing it
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Checks if the provided password matches the stored hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Category model: For organizing products (e.g., "Men's T-Shirts", "Dresses")
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False) # URL-friendly name

    # Relationship: a category can have many products
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

# Product model: Represents a single item for sale
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False) # URL-friendly name
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(200), nullable=True) # Stores filename of the product image
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Product {self.name}>'

# CartItem model: Represents an item in a user's shopping cart
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Product
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Product:{self.product_id} Qty:{self.quantity}>'

# Order model: Represents a completed order by a user
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending') # e.g., Pending, Shipped, Delivered

    # Relationship: an order can have multiple order items
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id} User:{self.user_id} Total:{self.total_amount}>'

# OrderItem model: Represents a single product within an order
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Price at the time of order

    # Relationship to Product
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id} Qty:{self.quantity}>'
