import os
import random
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import func
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Import models
from models import db, Booking, Driver, Contact, User

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a random secret key

# Configure SQLite database for local development
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transport.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add sample drivers if none exist
    if Driver.query.count() == 0:
        drivers = [
            Driver(name="Ramesh Kamthe", phone="+919876543210", vehicle="Tata Ace", plate="MH 12 AB 1234"),
            Driver(name="Mahesh Savant", phone="+919988776655", vehicle="Mahindra Bolero", plate="MH 12 CD 5678")
        ]
        db.session.add_all(drivers)
        db.session.commit()
        print("Added sample drivers")
    
    # Check if admin user exists, create if not
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password("10122003")  # Admin password
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")

# Home route
@app.route('/')
def index():
    app.logger.debug("Serving home page")
    return render_template('home.html')

# Add Booking route to display the form
@app.route('/booking')
def booking():
    app.logger.debug("Serving booking page")
    return render_template('index.html')

# Add Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    app.logger.debug("Serving contact page")
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        new_contact = Contact(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(new_contact)
        db.session.commit()
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# API for price calculation
@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    data = request.json
    pickup = data.get('pickup', '')
    dropoff = data.get('dropoff', '')
    quantity = float(data.get('quantity', 0))
    
    # Simple distance calculation (mock)
    pickup_len = len(pickup.strip())
    dropoff_len = len(dropoff.strip())
    distance = abs(pickup_len - dropoff_len) + 5  # Mock distance calculation
    
    # Calculate price based on distance and quantity
    base_price = distance * PRICE_PER_KM
    quantity_price = quantity * PRICE_PER_UNIT
    total_price = base_price + quantity_price
    
    return jsonify({
        'distance': distance,
        'price': total_price
    })

# API for booking
@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    pickup = request.form.get('pickup')
    dropoff = request.form.get('dropoff')
    quantity = float(request.form.get('quantity'))
    price = float(request.form.get('price'))
    
    # Generate a booking ID (random letters and numbers)
    booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # Assign a random driver
    driver = random.choice(Driver.query.all())
    
    # Create new booking
    new_booking = Booking(
        id=booking_id,
        name=name,
        email=email,
        phone=phone,
        pickup=pickup,
        dropoff=dropoff,
        quantity=quantity,
        price=price,
        driver_id=driver.id
    )
    db.session.add(new_booking)
    db.session.commit()
    
    # Return the booking details including driver info
    booking_details = new_booking.to_dict()
    
    return render_template('tracking.html', booking=booking_details)

# Tracking route
@app.route('/tracking/<booking_id>')
def tracking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        return render_template('tracking.html', booking=booking.to_dict())
    return "Booking not found", 404

# Add a reporting page
@app.route('/reports')
@login_required
def reports():
    # Check if user is admin
    if not current_user.is_admin:
        flash('You need admin privileges to access reports', 'danger')
        return redirect(url_for('index'))
    # Calculate time periods
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Query bookings for different time periods
    today_bookings = Booking.query.filter(func.date(Booking.timestamp) == today).all()
    week_bookings = Booking.query.filter(func.date(Booking.timestamp) >= week_start).all()
    month_bookings = Booking.query.filter(func.date(Booking.timestamp) >= month_start).all()
    
    # Calculate totals
    today_total = sum(booking.price for booking in today_bookings)
    week_total = sum(booking.price for booking in week_bookings)
    month_total = sum(booking.price for booking in month_bookings)
    
    return render_template('reports.html', 
                          today_bookings=today_bookings,
                          week_bookings=week_bookings, 
                          month_bookings=month_bookings,
                          today_total=today_total,
                          week_total=week_total,
                          month_total=month_total)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        account_type = request.form.get('account_type')
        admin_password = request.form.get('admin_password')
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('signup.html')
            
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        # Check admin password if applying for admin account
        is_admin = False
        if account_type == 'admin':
            if admin_password != '10122003':
                flash('Invalid admin password', 'danger')
                return render_template('signup.html')
            is_admin = True
            
        # Create new user
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('index'))
        
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

# Distance-based pricing (mock) - in Rupees
PRICE_PER_KM = 40  # ₹40 per km
PRICE_PER_UNIT = 100  # ₹100 per unit

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)