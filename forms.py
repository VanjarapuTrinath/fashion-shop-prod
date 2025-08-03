# fashion-shop/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models import User, Category # Import models to use for validation
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired # NEW IMPORTS
from models import User, Category # Import models to use for validation
# User Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    # Custom validation to check if username or email already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# User Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Add Product Form (for admin)
class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    slug = StringField('Product Slug (URL friendly)', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    # For category, we'll dynamically populate choices in the route
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    # UPDATED: Use FileField for direct image upload
    image_file = FileField('Product Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    available = BooleanField('Available for Sale', default=True)
    submit = SubmitField('Add Product')

    # Custom validation for slug uniqueness
    def validate_slug(self, slug):
        from models import Product # Import here to avoid circular dependency
        product = Product.query.filter_by(slug=slug.data).first()
        if product:
            raise ValidationError('That slug is already used by another product. Please choose a unique one.')

# Checkout Form
class CheckoutForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Shipping Address', validators=[DataRequired(), Length(max=250)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=20)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Place Order')