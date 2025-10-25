from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
import traceback
from sqlalchemy import inspect, text

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')

# Configure database - use DATABASE_URL environment variable if available (for Render)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///service_portal.db')
# Fix for PostgreSQL on Render (if needed)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    requests = db.relationship('ServiceRequest', backref='service', lazy=True)
    
    def __repr__(self):
        return f'<Service {self.name}>'

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    urgency = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServiceRequest {self.id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    service_type = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class ClientResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    accepted = db.Column(db.Boolean, default=False)
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)

    request = db.relationship('ServiceRequest', backref=db.backref('responses', lazy=True))
    client = db.relationship('User')

# Routes
@app.route('/')
def index():
    # If client is logged in, show only their service
    if session.get('role') == 'client' and session.get('service_type'):
        service = Service.query.filter_by(name=session.get('service_type')).first()
        if service:
            services = [service]
        else:
            services = []
    else:
        # Show all services for regular users and non-logged in users
        services = Service.query.all()
    
    return render_template('index.html', services=services)

@app.route('/service/<int:service_id>')
def service_form(service_id):
    if not session.get('user_id'):
        next_url = url_for('service_form', service_id=service_id)
        return redirect(url_for('login', next=next_url))

    service = Service.query.get_or_404(service_id)
    return render_template('service_form.html', service=service)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        if not session.get('user_id'):
            service_id = request.form.get('service_id')
            next_url = url_for('service_form', service_id=service_id) if service_id else url_for('index')
            return redirect(url_for('login', next=next_url))

        service_id = request.form.get('service_id')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        address = request.form.get('address')
        description = request.form.get('description')
        urgency = request.form.get('urgency')
        
        new_request = ServiceRequest(
            service_id=service_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            address=address,
            description=description,
            urgency=urgency
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        return render_template('confirmation.html', request=new_request)

@app.route('/get_services')
def get_services():
    services = Service.query.all()
    service_list = [{'id': service.id, 'name': service.name} for service in services]
    return jsonify(service_list)

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            next_page = request.form.get('next') or url_for('index')
            role = request.form.get('role', 'user')
            
            if not username or not email or not password:
                flash('Please fill in all required fields', 'warning')
                return redirect(url_for('register'))

            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash('A user with that username or email already exists', 'danger')
                return redirect(url_for('register'))

            service_type = None
            if role == 'client':
                service_type = request.form.get('service_type')
                if not service_type:
                    flash('Please select a service type for client registration', 'warning')
                    return redirect(url_for('register'))

            user = User(username=username, email=email, role=role, service_type=service_type)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login', next=next_page))
        except Exception as e:
            app.logger.error(f'Registration error: {str(e)}')
            app.logger.exception('Full traceback:')
            flash(f'An unexpected error occurred while registering: {str(e)}', 'danger')
            return redirect(url_for('register'))

    services = Service.query.all()
    return render_template('register.html', services=services)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username_or_email = request.form.get('username_or_email')
            password = request.form.get('password')
            next_page = request.form.get('next') or url_for('index')

            user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session['service_type'] = user.service_type
                flash('Logged in successfully', 'success')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials', 'danger')
                return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f'Login error: {str(e)}')
            app.logger.exception('Full traceback:')
            flash(f'An unexpected error occurred while logging in: {str(e)}', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/client/dashboard')
def client_dashboard():
    if not session.get('user_id') or session.get('role') != 'client':
        flash('You must be logged in as a client to access this page.', 'warning')
        return redirect(url_for('login', next=url_for('client_dashboard')))

    client_service_type = session.get('service_type')
    
    if not client_service_type:
        flash('Your account is not associated with any service type. Please contact support.', 'warning')
        return redirect(url_for('index'))

    service = Service.query.filter_by(name=client_service_type).first()
    
    if not service:
        flash(f'No service found for your service type: {client_service_type}', 'warning')
        return redirect(url_for('index'))

    # Get statistics
    total_requests = ServiceRequest.query.filter_by(service_id=service.id).count()
    pending_requests = ServiceRequest.query.filter_by(service_id=service.id).count()
    
    # Get recent requests
    requests = ServiceRequest.query.filter_by(service_id=service.id).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template('client_dashboard.html', 
                         requests=requests, 
                         client_service_type=client_service_type,
                         total_requests=total_requests,
                         pending_requests=pending_requests)

@app.route('/client/requests')
def client_requests():
    if not session.get('user_id') or session.get('role') != 'client':
        flash('You must be logged in as a client to access this page.', 'warning')
        return redirect(url_for('login', next=url_for('client_requests')))

    client_service_type = session.get('service_type')
    
    if not client_service_type:
        flash('Your account is not associated with any service type. Please contact support.', 'warning')
        return redirect(url_for('index'))

    service = Service.query.filter_by(name=client_service_type).first()
    
    if not service:
        flash(f'No service found for your service type: {client_service_type}', 'warning')
        return redirect(url_for('index'))

    requests = ServiceRequest.query.filter_by(service_id=service.id).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template('client_requests.html', requests=requests, client_service_type=client_service_type)

@app.route('/client/request/<int:req_id>/accept', methods=['POST'])
def client_accept_request(req_id):
    if not session.get('user_id') or session.get('role') != 'client':
        return redirect(url_for('login', next=url_for('client_requests')))

    req = ServiceRequest.query.get_or_404(req_id)
    
    client_service_type = session.get('service_type')
    service = Service.query.filter_by(name=client_service_type).first()
    
    if not service or req.service_id != service.id:
        flash('You are not authorized to accept this request.', 'danger')
        return redirect(url_for('client_requests'))

    response = ClientResponse.query.filter_by(request_id=req.id, client_id=session.get('user_id')).first()
    if not response:
        response = ClientResponse(request_id=req.id, client_id=session.get('user_id'), accepted=True, message='Accepted')
        db.session.add(response)
    else:
        response.accepted = True
        response.responded_at = datetime.utcnow()

    db.session.commit()
    flash('Request accepted successfully!', 'success')
    return redirect(url_for('client_requests'))

@app.route('/client/request/<int:req_id>/respond', methods=['GET', 'POST'])
def client_respond_request(req_id):
    if not session.get('user_id') or session.get('role') != 'client':
        return redirect(url_for('login', next=url_for('client_requests')))

    req = ServiceRequest.query.get_or_404(req_id)
    
    client_service_type = session.get('service_type')
    service = Service.query.filter_by(name=client_service_type).first()
    
    if not service or req.service_id != service.id:
        flash('You are not authorized to respond to this request.', 'danger')
        return redirect(url_for('client_requests'))

    if request.method == 'POST':
        message = request.form.get('message')
        response = ClientResponse(request_id=req.id, client_id=session.get('user_id'), message=message, accepted=False)
        db.session.add(response)
        db.session.commit()
        flash('Response sent successfully!', 'success')
        return redirect(url_for('client_requests'))

    return render_template('client_respond.html', request=req)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('service_type', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/test')
def test():
    return render_template('test.html')

def initialize_database():
    with app.app_context():
        db.create_all()
        
        try:
            inspector = inspect(db.engine)
            if 'user' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('user')]
                
                if 'role' not in cols:
                    try:
                        with db.engine.connect() as conn:
                            if 'sqlite' in db.engine.url.drivername:
                                conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                            else:
                                conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                            conn.commit()
                        print("Added 'role' column to user table")
                    except Exception as e:
                        print(f"Error adding role column: {e}")
                
                if 'service_type' not in cols:
                    try:
                        with db.engine.connect() as conn:
                            if 'sqlite' in db.engine.url.drivername:
                                conn.execute(text("ALTER TABLE user ADD COLUMN service_type VARCHAR(100)"))
                            else:
                                conn.execute(text("ALTER TABLE user ADD COLUMN service_type VARCHAR(100)"))
                            conn.commit()
                        print("Added 'service_type' column to user table")
                    except Exception as e:
                        print(f"Error adding service_type column: {e}")
                        
        except Exception as e:
            print(f'Could not ensure columns: {e}')
            
        if not Service.query.first():
            services_data = [
                {"name": "Plumbing", "description": "Water leaks, pipe repairs, installations"},
                {"name": "Electrical", "description": "Wiring, electrical repairs, installations"},
                {"name": "Carpentry", "description": "Furniture repairs, installations, woodwork"},
                {"name": "Cleaning", "description": "Home cleaning, deep cleaning services"},
                {"name": "Gardening", "description": "Garden maintenance, landscaping"},
                {"name": "Automotive", "description": "Car repair, maintenance, towing"},
                {"name": "Ambulance", "description": "Emergency medical transport"},
                {"name": "Police", "description": "Emergency law enforcement assistance"},
                {"name": "Fire Fighter", "description": "Fire emergency and rescue services"}
            ]
            
            for service_data in services_data:
                service = Service(name=service_data["name"], description=service_data["description"])
                db.session.add(service)
            
            db.session.commit()
            print("Database initialized with sample data!")

with app.app_context():
    initialize_database()

if not app.debug:
    try:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=3)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    except Exception:
        print('Could not set up file logging')

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception('Unhandled Exception:')
    try:
        with open('logs/error.log', 'a', encoding='utf-8') as f:
            traceback.print_exc(file=f)
    except Exception:
        pass
    return render_template('error.html', message=str(error)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)