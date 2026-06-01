import os
import random
import string
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, g

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a random secret key

# Create a class to mimic Flask-Login's UserMixin
class User:
    def __init__(self, user_dict=None):
        self.id = user_dict.get('id') if user_dict else None
        self.username = user_dict.get('username') if user_dict else None
        self.email = user_dict.get('email') if user_dict else None
        self.is_admin = user_dict.get('is_admin', False) if user_dict else False
        self.is_authenticated = user_dict is not None
        self.is_active = True
        self.is_anonymous = user_dict is None

    def get_id(self):
        return str(self.id) if self.id else None

# Add a context processor to make current_user available to all templates
@app.context_processor
def inject_user():
    user_dict = session.get('current_user')
    return {'current_user': User(user_dict) if user_dict else User()}

# Mock data for drivers
DRIVERS = [
    {
        "id": 1,
        "name": "Ramesh Kamthe",
        "phone": "+919876543210",
        "vehicle": "Tata Ace",
        "plate": "MH 12 AB 1234"
    },
    {
        "id": 2,
        "name": "Mahesh Savant",
        "phone": "+919988776655",
        "vehicle": "Mahindra Bolero",
        "plate": "MH 12 CD 5678"
    }
]

# Pricing constants (in Rupees)
PRICE_PER_KM = 40  # ₹40 per km
PRICE_PER_UNIT = 100  # ₹100 per unit

# Initialize storage in session
def init_storage():
    if 'bookings' not in session:
        session['bookings'] = []
    if 'contacts' not in session:
        session['contacts'] = []
    if 'users' not in session:
        session['users'] = [{
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'password': '10122003',  # In a real app, this would be hashed
            'is_admin': True
        }]
    if 'current_user' not in session:
        session['current_user'] = None

# Home route
@app.route('/')
def index():
    init_storage()
    return render_template('home.html')

# Add Booking route to display the form
@app.route('/booking')
def booking():
    init_storage()
    return render_template('index.html')

# Add Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    init_storage()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        contact_entry = {
            'id': len(session['contacts']) + 1,
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        contacts = session['contacts']
        contacts.append(contact_entry)
        session['contacts'] = contacts
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# API for price calculation
@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    app.logger.debug("Calculate price route accessed")
    
    # Handle both form data and JSON requests
    if request.is_json:
        data = request.json
        app.logger.debug("JSON data received")
    else:
        data = request.form
        app.logger.debug("Form data received: %s", data)
    
    pickup = data.get('pickup', '')
    dropoff = data.get('dropoff', '')
    
    # Convert quantity to float, handle possible errors
    try:
        quantity = float(data.get('quantity', 0))
    except (ValueError, TypeError):
        app.logger.error("Invalid quantity value: %s", data.get('quantity'))
        quantity = 0
    
    app.logger.debug("Pickup: %s, Dropoff: %s, Quantity: %s", pickup, dropoff, quantity)
    
    # Simple distance calculation (mock)
    pickup_len = len(pickup.strip())
    dropoff_len = len(dropoff.strip())
    distance = abs(pickup_len - dropoff_len) + 5  # Mock distance calculation
    
    # Calculate price based on distance and quantity
    base_price = distance * PRICE_PER_KM
    quantity_price = quantity * PRICE_PER_UNIT
    total_price = base_price + quantity_price
    
    app.logger.debug("Calculated: Distance=%s, Price=%s", distance, total_price)
    
    return jsonify({
        'distance': distance,
        'price': total_price
    })

# API for booking
@app.route('/book', methods=['POST'])
def book():
    app.logger.debug("Book route accessed")
    init_storage()
    
    # Log the request data to help debug
    app.logger.debug("Form data: %s", request.form)
    
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        pickup = request.form.get('pickup')
        dropoff = request.form.get('dropoff')
        
        # Safely handle quantity conversion
        try:
            quantity = float(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            app.logger.error("Invalid quantity value: %s", request.form.get('quantity'))
            quantity = 0
            
        # Safely handle price conversion
        try:
            price = float(request.form.get('price', 0))
        except (ValueError, TypeError):
            app.logger.error("Invalid price value: %s", request.form.get('price'))
            price = 0
            
        app.logger.debug("Booking details: Name=%s, Email=%s, Phone=%s, Pickup=%s, Dropoff=%s, Quantity=%s, Price=%s",
                        name, email, phone, pickup, dropoff, quantity, price)
        
        # Generate a booking ID (random letters and numbers)
        booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Assign a random driver
        driver = random.choice(DRIVERS)
        
        # Create new booking
        new_booking = {
            'id': booking_id,
            'name': name,
            'email': email,
            'phone': phone,
            'pickup': pickup,
            'dropoff': dropoff,
            'quantity': quantity,
            'price': price,
            'status': 'Confirmed',
            'driver': driver,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        bookings = session['bookings']
        bookings.append(new_booking)
        session['bookings'] = bookings
        
        app.logger.debug("Booking created successfully: %s", new_booking)
        
        # Return JSON response for the AJAX call
        return jsonify({
            'success': True,
            'booking': new_booking
        })
        
    except Exception as e:
        app.logger.error("Error creating booking: %s", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Tracking route
@app.route('/tracking/<booking_id>')
def tracking(booking_id):
    init_storage()
    booking = None
    for b in session['bookings']:
        if b['id'] == booking_id:
            booking = b
            break
            
    if booking:
        return render_template('tracking.html', booking=booking)
    return "Booking not found", 404

# Add a reporting page
@app.route('/reports')
def reports():
    app.logger.debug("Reports route accessed")
    init_storage()
    
    # Check if user is logged in and is admin
    user_dict = session.get('current_user')
    if not user_dict or not isinstance(user_dict, dict) or not user_dict.get('is_admin', False):
        flash('You need admin privileges to access reports', 'danger')
        return redirect(url_for('index'))
        
    # All bookings are "today" for simplicity in this example
    bookings = session['bookings']
    
    return render_template('reports.html', 
                          today_bookings=bookings,
                          week_bookings=bookings, 
                          month_bookings=bookings,
                          today_total=sum(b['price'] for b in bookings),
                          week_total=sum(b['price'] for b in bookings),
                          month_total=sum(b['price'] for b in bookings))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug("Login route accessed")
    init_storage()
    
    # Only redirect if we have an actual user object, not None
    user_dict = session.get('current_user')
    if user_dict and isinstance(user_dict, dict) and 'id' in user_dict:
        app.logger.debug("User already logged in, redirecting to index")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = None
        for u in session['users']:
            if u['username'] == username and u['password'] == password:
                user = u
                break
        
        if user:
            session['current_user'] = user
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    init_storage()
    session['current_user'] = None
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    app.logger.debug("Signup route accessed")
    init_storage()
    
    # Only redirect if we have an actual user object, not None
    user_dict = session.get('current_user')
    if user_dict and isinstance(user_dict, dict) and 'id' in user_dict:
        app.logger.debug("User already logged in, redirecting to index")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        account_type = request.form.get('account_type')
        admin_password = request.form.get('admin_password')
        
        # Check if username or email already exists
        for u in session['users']:
            if u['username'] == username or u['email'] == email:
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
        user = {
            'id': len(session['users']) + 1,
            'username': username,
            'email': email,
            'password': password,
            'is_admin': is_admin
        }
        
        users = session['users']
        users.append(user)
        session['users'] = users
        
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/users')
def users():
    app.logger.debug("Users route accessed")
    init_storage()
    
    user_dict = session.get('current_user')
    if not user_dict or not isinstance(user_dict, dict) or not user_dict.get('is_admin', False):
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('index'))
        
    return render_template('users.html', users=session['users'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)