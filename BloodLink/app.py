import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import json
import csv
import io
from collections import defaultdict
from sqlalchemy import func, and_, or_
from werkzeug.utils import secure_filename
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bloodlink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Allowed file extensions for blood test reports
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Chatbot Adapter Interface
class ChatbotAdapter:
    def __init__(self):
        self.provider = os.environ.get('MEDICAL_CHATBOT_PROVIDER', '')
        self.api_key = os.environ.get('MEDICAL_CHATBOT_API_KEY', '')
        
    def send(self, message: str, user_context: dict) -> str:
        if not self.provider or not self.api_key:
            return "Chatbot is currently unavailable. Please check configuration."
        
        # Mock response for demonstration - replace with actual API integration
        if self.provider == 'openai':
            return f"Medical AI: Based on your query '{message}', I recommend consulting with a healthcare professional for personalized advice."
        elif self.provider == 'infermedica':
            return f"Medical Assistant: Regarding '{message}', please note this is general information and not a substitute for professional medical advice."
        else:
            return "I'm here to help with general health information. Please consult healthcare professionals for specific medical advice."

chatbot = ChatbotAdapter()

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    diseases = db.Column(db.Text)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    
    # New fields for blood donor registration improvement
    test_hospital_name = db.Column(db.String(200))
    blood_report_filename = db.Column(db.String(255))
    report_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    report_submitted_at = db.Column(db.DateTime)
    approved_by_hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    is_verified_donor = db.Column(db.Boolean, default=False)
    
    # Relationships
    blood_usage = db.relationship('BloodUsage', backref='donor', lazy=True)
    approved_by_hospital = db.relationship('Hospital', foreign_keys=[approved_by_hospital_id], backref='approved_donors')

class Hospital(UserMixin, db.Model):
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    hospital_code = db.Column(db.String(50), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='hospital')
    
    # Relationships
    blood_usage = db.relationship('BloodUsage', backref='hospital', lazy=True)

class BloodUsage(db.Model):
    __tablename__ = 'blood_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    # Check if it's a regular user
    user = User.query.get(int(user_id))
    if user:
        return user
    # Check if it's a hospital
    hospital = Hospital.query.get(int(user_id))
    return hospital

# Helper function to get valid hospital codes
def get_valid_hospital_codes():
    codes = os.environ.get('HOSPITAL_CODES', 'HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001')
    return [code.strip() for code in codes.split(',')]

# Helper function to check if report is still pending (within 30 minutes)
def is_report_pending(user):
    if not user.report_submitted_at:
        return False
    time_diff = datetime.utcnow() - user.report_submitted_at
    return time_diff < timedelta(minutes=30) and user.report_status == 'pending'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        
        # Handle custom gender input
        if gender == 'Other' and 'other_gender' in request.form:
            other_gender = request.form['other_gender'].strip()
            if other_gender:
                gender = other_gender
        
        blood_group = request.form['blood_group']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        contact_number = request.form['contact_number']
        diseases = request.form['diseases']
        email = request.form['email']
        password = request.form['password']
        test_hospital_name = request.form['test_hospital_name']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('register'))
        
        # Handle file upload
        blood_report_filename = None
        if 'blood_report' in request.files:
            file = request.files['blood_report']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(os.path.join(app.root_path, file_path))
                blood_report_filename = filename
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            name=name, age=age, gender=gender, blood_group=blood_group,
            city=city, state=state, pincode=pincode, contact_number=contact_number,
            diseases=diseases, email=email, password_hash=password_hash,
            test_hospital_name=test_hospital_name,
            blood_report_filename=blood_report_filename,
            report_submitted_at=datetime.utcnow() if blood_report_filename else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/Hospital-Register', methods=['GET', 'POST'])
def hospital_register():
    if request.method == 'POST':
        name = request.form['name']
        hospital_code = request.form['hospital_code']
        city = request.form['city']
        state = request.form['state']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password = request.form['password']
        
        # Validate hospital code
        if hospital_code not in get_valid_hospital_codes():
            flash('Invalid hospital code. Please contact administrator.', 'error')
            return redirect(url_for('hospital_register'))
        
        # Check if hospital already exists
        if Hospital.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('hospital_register'))
        
        if Hospital.query.filter_by(hospital_code=hospital_code).first():
            flash('Hospital code already in use.', 'error')
            return redirect(url_for('hospital_register'))
        
        # Create new hospital
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        hospital = Hospital(
            name=name, hospital_code=hospital_code, city=city, state=state,
            contact_number=contact_number, email=email, password_hash=password_hash
        )
        
        db.session.add(hospital)
        db.session.commit()
        
        flash('Hospital registration successful! Please login.', 'success')
        return redirect(url_for('hospital_login'))
    
    return render_template('hospital_register.html')

@app.route('/Hospital-Login', methods=['GET', 'POST'])
def hospital_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        hospital = Hospital.query.filter_by(email=email).first()
        
        if hospital and bcrypt.check_password_hash(hospital.password_hash, password):
            login_user(hospital)
            return redirect(url_for('hospital_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('hospital_login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'hospital':
        return redirect(url_for('hospital_dashboard'))
    
    # Get blood usage stats for the user
    usage_records = BloodUsage.query.filter_by(donor_id=current_user.id).all()
    usage_count = len(usage_records)
    
    # Check if report is still pending
    report_pending = is_report_pending(current_user)
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         usage_records=usage_records, 
                         usage_count=usage_count,
                         report_pending=report_pending)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = int(request.form['age'])
        current_user.gender = request.form['gender']
        current_user.blood_group = request.form['blood_group']
        current_user.city = request.form['city']
        current_user.state = request.form['state']
        current_user.pincode = request.form['pincode']
        current_user.contact_number = request.form['contact_number']
        current_user.diseases = request.form['diseases']
        current_user.test_hospital_name = request.form['test_hospital_name']
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/remove_report', methods=['POST'])
@login_required
def remove_report():
    if current_user.role != 'user':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Only allow removal if report is still pending and within 30 minutes
    if is_report_pending(current_user):
        # Delete the file
        if current_user.blood_report_filename:
            file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], current_user.blood_report_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Reset report fields
        current_user.blood_report_filename = None
        current_user.report_submitted_at = None
        current_user.report_status = 'pending'
        
        db.session.commit()
        flash('Blood test report removed successfully!', 'success')
    else:
        flash('Report cannot be removed at this time.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/hospital/dashboard')
@login_required
def hospital_dashboard():
    if current_user.role != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Get search parameters
    blood_group = request.args.get('blood_group', '')
    city = request.args.get('city', '')
    state = request.args.get('state', '')
    
    # Build query - only show verified donors
    query = User.query.filter_by(role='user', is_verified_donor=True)
    
    if blood_group:
        query = query.filter(User.blood_group == blood_group)
    if city:
        query = query.filter(User.city.ilike(f'%{city}%'))
    if state:
        query = query.filter(User.state.ilike(f'%{state}%'))
    
    donors = query.all()
    
    # Get pending approvals for this hospital
    pending_approvals = User.query.filter(
        User.test_hospital_name.ilike(f'%{current_user.name}%'),
        User.report_status == 'pending',
        User.blood_report_filename.isnot(None)
    ).all()
    
    # Get unique blood groups for filter dropdown
    blood_groups = db.session.query(User.blood_group).filter_by(role='user', is_verified_donor=True).distinct().all()
    blood_groups = [bg[0] for bg in blood_groups]
    
    return render_template('hospital_dashboard.html', 
                         donors=donors, 
                         blood_groups=blood_groups,
                         search_blood_group=blood_group,
                         search_city=city,
                         search_state=state,
                         pending_approvals=pending_approvals)

@app.route('/hospital/approve_donor/<int:donor_id>', methods=['POST'])
@login_required
def approve_donor(donor_id):
    if current_user.role != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    donor = User.query.get_or_404(donor_id)
    action = request.form.get('action')
    
    if action == 'approve':
        donor.report_status = 'approved'
        donor.is_verified_donor = True
        donor.approved_by_hospital_id = current_user.id
        flash(f'Donor {donor.name} has been approved!', 'success')
    elif action == 'reject':
        donor.report_status = 'rejected'
        donor.is_verified_donor = False
        flash(f'Donor {donor.name} has been rejected.', 'warning')
    
    db.session.commit()
    return redirect(url_for('hospital_dashboard'))

@app.route('/hospital/usage/new')
@login_required
def new_usage():
    if current_user.role != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    donor_id = request.args.get('donor_id')
    if not donor_id:
        flash('Donor ID required', 'error')
        return redirect(url_for('hospital_dashboard'))
    
    donor = User.query.get_or_404(donor_id)
    return render_template('usage_form.html', donor=donor)

@app.route('/hospital/usage/create', methods=['POST'])
@login_required
def create_usage():
    if current_user.role != 'hospital':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    donor_id = request.form['donor_id']
    notes = request.form['notes']
    
    usage = BloodUsage(
        donor_id=donor_id,
        hospital_id=current_user.id,
        notes=notes
    )
    
    db.session.add(usage)
    db.session.commit()
    
    flash('Blood usage record created successfully!', 'success')
    return redirect(url_for('hospital_dashboard'))

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_api():
    data = request.get_json()
    message = data.get('message', '')
    context = data.get('context', {})
    
    # Add user context
    user_context = {
        'user_id': current_user.id,
        'user_role': current_user.role,
        'user_name': current_user.name if hasattr(current_user, 'name') else 'User'
    }
    user_context.update(context)
    
    reply = chatbot.send(message, user_context)
    
    return jsonify({'reply': reply})

@app.route('/api/dashboard_stats')
@login_required
def dashboard_stats():
    if current_user.role == 'hospital':
        # Hospital stats
        total_donors = User.query.filter_by(role='user', is_verified_donor=True).count()
        pending_approvals = User.query.filter(
            User.test_hospital_name.ilike(f'%{current_user.name}%'),
            User.report_status == 'pending'
        ).count()
        blood_usage_count = BloodUsage.query.filter_by(hospital_id=current_user.id).count()
        
        return jsonify({
            'total_donors': total_donors,
            'pending_approvals': pending_approvals,
            'blood_usage_count': blood_usage_count
        })
    else:
        # Donor stats
        usage_count = BloodUsage.query.filter_by(donor_id=current_user.id).count()
        is_verified = current_user.is_verified_donor
        report_status = current_user.report_status
        
        return jsonify({
            'usage_count': usage_count,
            'is_verified': is_verified,
            'report_status': report_status
        })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)