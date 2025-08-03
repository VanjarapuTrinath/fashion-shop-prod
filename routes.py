# fashion-shop/routes.py

from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from app import app, db # Import app and db from our main app.py
from models import User, Product, Category, CartItem, Order, OrderItem
from forms import RegistrationForm, LoginForm, AddProductForm, CheckoutForm
from flask_login import login_user, current_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename # For secure filename handling
from werkzeug.datastructures import FileStorage # NEW IMPORT

# Helper function to check allowed image file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Public Routes ---

@app.route('/')
@app.route('/home')
def home():
    products = Product.query.filter_by(available=True).order_by(Product.created_at.desc()).limit(8).all()
    # Pass a form instance for CSRF protection
    form = LoginForm()
    return render_template('index.html', products=products, form=form)

@app.route('/products')
def products():
    products = Product.query.filter_by(available=True).order_by(Product.name).all()
    categories = Category.query.all()
    # Pass a form instance for CSRF protection
    form = LoginForm()
    return render_template('products.html', products=products, categories=categories, form=form)

@app.route('/products/category/<string:slug>')
def products_by_category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    products = Product.query.filter_by(category=category, available=True).order_by(Product.name).all()
    categories = Category.query.all()
    # Pass a form instance for CSRF protection
    form = LoginForm()
    return render_template('products.html', products=products, categories=categories, current_category=category, form=form)

@app.route('/product/<string:slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, available=True).first_or_404()
    # Pass a form instance for CSRF protection
    form = LoginForm()
    return render_template('product_detail.html', product=product, form=form)

# --- User Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page or url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# --- Cart Routes (FORM-BASED) ---

# This route handles form submissions from the product listing and detail pages
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)

    try:
        product_id = int(product_id)
        quantity = int(quantity)
        if quantity <= 0:
            flash('Quantity must be positive.', 'danger')
            return redirect(request.referrer or url_for('products'))
    except (ValueError, TypeError):
        flash('Invalid product ID or quantity.', 'danger')
        return redirect(request.referrer or url_for('products'))

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(request.referrer or url_for('products'))
    if not product.available:
        flash('Product not available.', 'danger')
        return redirect(request.referrer or url_for('products'))
    if product.stock < quantity:
        flash(f'Not enough stock for {product.name}. Available: {product.stock}.', 'danger')
        return redirect(request.referrer or url_for('products'))

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        if product.stock < (cart_item.quantity + quantity):
            flash(f'Adding more would exceed stock. Max available: {product.stock - cart_item.quantity}', 'danger')
            return redirect(request.referrer or url_for('products'))
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    try:
        db.session.commit()
        flash(f'{product.name} added to cart successfully!', 'success')
        return redirect(url_for('cart'))
    except Exception:
        db.session.rollback()
        flash('Failed to add item to cart due to a database error.', 'danger')
        return redirect(request.referrer or url_for('products'))

@app.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    item_id = request.form.get('item_id')

    try:
        item_id = int(item_id)
    except (ValueError, TypeError):
        flash('Invalid cart item ID.', 'danger')
        return redirect(url_for('cart'))

    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        flash('Cart item not found.', 'danger')
        return redirect(url_for('cart'))

    try:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
        return redirect(url_for('cart'))
    except Exception:
        db.session.rollback()
        flash('Failed to remove item from cart due to a database error.', 'danger')
        return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart_item():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity')

    try:
        item_id = int(item_id)
        quantity = int(quantity)
        if quantity <= 0:
            flash('Quantity must be positive.', 'danger')
            return redirect(url_for('cart'))
    except (ValueError, TypeError):
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('cart'))

    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not cart_item:
        flash('Cart item not found.', 'danger')
        return redirect(url_for('cart'))

    if cart_item.product.stock < quantity:
        flash(f'Not enough stock for {cart_item.product.name}. Max available: {cart_item.product.stock}', 'danger')
        return redirect(url_for('cart'))

    try:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated.', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to update cart due to a database error.', 'danger')

    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    # Pass a form instance for CSRF protection
    form = LoginForm()
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total, form=form)

# --- Checkout & Order Routes ---

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('products'))

    form = CheckoutForm()
    if form.validate_on_submit():
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        shipping_address = f"{form.address.data}, {form.city.data}, {form.postal_code.data}"

        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='Pending'
        )
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)

            item.product.stock -= item.quantity
            db.session.delete(item)

        db.session.commit()
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('order_history'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')

    if current_user.email and not form.email.data:
        form.email.data = current_user.email
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', form=form, cart_items=cart_items, cart_total=cart_total)

@app.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', orders=orders)

# --- Admin Routes ---

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        abort(403)

    form = AddProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

    if form.validate_on_submit():
        image_file = form.image_file.data
        if isinstance(image_file, FileStorage) and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename_to_save = filename
        else:
            image_filename_to_save = None

        product = Product(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category.data,
            image_filename=image_filename_to_save,
            available=form.available.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('admin_add_product.html', form=form)

# Error Handlers (Optional but good practice)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403