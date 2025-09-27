from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from authlib.integrations.flask_client import OAuth
from app.models import User, Customer, Order, db
from app.services import sms_service
import os

# Initialize OAuth
oauth = OAuth()

# Create main blueprint
main_bp = Blueprint('main', __name__)

def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    oauth.init_app(app)
    
    # Check if Google OAuth credentials are configured
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print('Warning: Google OAuth credentials not configured')
        return
    
    try: # pragma: no cover
        oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://oauth2.googleapis.com/token', 
            userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
            client_kwargs={
                'scope': 'openid email profile',
                'token_endpoint_auth_method': 'client_secret_post'}
        )
        print('Google OAuth configured successfully')
    except Exception as e:
        print(f'Google OAuth configuration failed: {e}')

@main_bp.route('/')

def index():
    return render_template('index.html')

@main_bp.route('/login')
def login():
    """Initiate Google OAuth login"""
    # Check if OAuth is configured
    if 'google' not in oauth._clients:
        flash('Google OAuth is not configured. Please contact administrator.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        redirect_uri = url_for('main.auth_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        flash('Login service is currently unavailable.', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/callback')
def auth_callback(): # pragma: no cover
    """OAuth callback handler - manual approach"""
    print("=== DEBUG: Callback Route Started ===")
    print(f"Request args: {request.args}")
    
    try:
        if 'code' not in request.args:
            print("No authorization code received")
            flash('Authentication failed.', 'error')
            return redirect(url_for('main.index'))
        
        # token exchange
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = url_for('main.auth_callback', _external=True)
        code = request.args.get('code')
        
        print("exchanging code for token...")
        
        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        import requests
        token_response = requests.post(token_url, data=token_data)
        print(f"Token response status: {token_response.status_code}")
        
        if token_response.status_code != 200:
            print(f"Token exchange failed: {token_response.text}")
            flash('Authentication failed.', 'error')
            return redirect(url_for('main.index'))
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            print("No access token received")
            flash('Authentication failed.', 'error')
            return redirect(url_for('main.index'))
        
        # Get user info using access token
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        
        print(f"Userinfo response status: {userinfo_response.status_code}")
        
        if userinfo_response.status_code != 200:
            print(f"Userinfo request failed: {userinfo_response.text}")
            flash('Authentication failed.', 'error')
            return redirect(url_for('main.index'))
        
        user_info = userinfo_response.json()
        print(f"User info: {user_info}")
        
        # Process user information
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name')
        
        if not all([google_id, email, name]):
            print("Missing user information")
            flash('Authentication failed.', 'error')
            return redirect(url_for('main.index'))
        
        # Find or create user
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            user = User(
                google_id=google_id,
                email=email,
                name=name
            )
            db.session.add(user)
            db.session.commit()
            print(f"New user created: {email}")
        else:
            print(f"Existing user found: {email}")
        
        login_user(user)
        flash(f'Welcome, {user.name}!', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        print(f"Exception in callback route: {e}")
        import traceback
        traceback.print_exc()
        flash('Authentication failed.', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    customers = Customer.query.filter_by(created_by=current_user.id).order_by(Customer.created_at.desc()).all()
    orders = Order.query.filter_by(created_by=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard.html', customers=customers, orders=orders)

@main_bp.route('/customer', methods=['POST'])
@login_required
def create_customer():
    """Create a new customer"""
    try:
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not name or not phone:
            flash('Name and phone are required', 'error')
            return redirect(url_for('main.dashboard'))
        
        customer = Customer(name=name, phone=phone, created_by=current_user.id)
        db.session.add(customer)
        db.session.commit()
        
        flash(f'Customer "{name}" created successfully!', 'success')
        
    except Exception as e:
        flash('Error creating customer. Please try again.', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/order', methods=['POST'])
@login_required
def create_order():
    """Create a new order"""
    try:
        order_name = request.form.get('order_name', '').strip()
        price_str = request.form.get('price', '0')
        customer_id = request.form.get('customer_id')
        
        # Validation
        if not order_name or not customer_id:
            flash('Order name and customer selection are required', 'error')
            return redirect(url_for('main.dashboard'))
        
        try:
            price = float(price_str)
            if price <= 0:
                flash('Price must be greater than 0', 'error')
                return redirect(url_for('main.dashboard'))
        except ValueError:
            flash('Please enter a valid price', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Verify customer belongs to current user
        customer = Customer.query.filter_by(id=customer_id, created_by=current_user.id).first()
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Create order
        order = Order(
            order_name=order_name,
            price=price,
            customer_id=customer_id,
            created_by=current_user.id
        )
        db.session.add(order)
        db.session.commit()
        
        # Send SMS notification
        sms_sent = sms_service.send_order_confirmation(customer.phone, order_name, price)
        
        if sms_sent:
            flash(f'Order "{order_name}" created successfully! SMS sent to customer.', 'success')
        else:
            flash(f'Order "{order_name}" created successfully! But SMS failed to send.', 'warning')
        
    except Exception as e:
        flash('Error creating order. Please try again.', 'error')
    
    return redirect(url_for('main.dashboard'))

    

# API Routes
@main_bp.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Service is running'})

@main_bp.route('/api/customers')
@login_required
def api_get_customers():
    """API: Get all customers for current user"""
    customers = Customer.query.filter_by(created_by=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'created_at': c.created_at.isoformat(),
        'order_count': len(c.orders)
    } for c in customers])

@main_bp.route('/api/orders')
@login_required
def api_get_orders():
    """API: Get all orders for current user"""
    orders = Order.query.filter_by(created_by=current_user.id).all()
    return jsonify([order.to_dict() for order in orders])