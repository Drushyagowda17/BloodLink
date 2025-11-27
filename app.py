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
        self.provider = os.environ.get('MEDICAL_CHATBOT_PROVIDER', 'huggingface')
        self.api_key = os.environ.get('MEDICAL_CHATBOT_API_KEY', '')
        self.base_url = "https://api-inference.huggingface.co/models/"
        
    def send(self, message: str, user_context: dict) -> str:
        try:
            # Use free Hugging Face Inference API for medical questions
            if self.provider == 'huggingface':
                return self._query_huggingface(message)
            elif self.provider == 'openai' and self.api_key:
                return self._query_openai(message)
            else:
                return self._get_fallback_response(message)
        except Exception as e:
            print(f"Chatbot error: {e}")
            return self._get_fallback_response(message)
    
    def _query_huggingface(self, message: str) -> str:
        import requests
        
        # Use a medical-focused model from Hugging Face
        model_name = "microsoft/DialoGPT-medium"
        url = f"{self.base_url}{model_name}"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Prepare medical context prompt
        medical_prompt = f"""You are a helpful medical assistant. Please provide general health information for the following question. Always remind users to consult healthcare professionals for specific medical advice.

Question: {message}

Response:"""
        
        payload = {
            "inputs": medical_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extract only the response part
                    if 'Response:' in generated_text:
                        answer = generated_text.split('Response:')[-1].strip()
                        if answer:
                            return f"{answer}\n\n⚠️ This is general information only. Please consult a healthcare professional for personalized medical advice."
            
            # Fallback if API doesn't work as expected
            return self._get_medical_response(message)
            
        except requests.exceptions.RequestException:
            return self._get_medical_response(message)
    
    def _query_openai(self, message: str) -> str:
        # OpenAI integration (if API key is provided)
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful medical assistant. Provide general health information and always remind users to consult healthcare professionals for specific medical advice."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
        except:
            pass
        
        return self._get_medical_response(message)
    
    def _get_medical_response(self, message: str) -> str:
        """Generate comprehensive medical responses based on keywords and symptoms"""
        message_lower = message.lower()
        
        # Fever and temperature related
        if any(word in message_lower for word in ['fever', 'temperature', 'hot', 'burning', 'chills', 'shivering']):
            return """**Fever Management:**

🌡️ **Immediate Care:**
• Rest and stay hydrated with water, clear broths, or electrolyte solutions
• Take temperature every 4-6 hours
• Use acetaminophen or ibuprofen as directed on package
• Apply cool, damp cloths to forehead and wrists
• Wear light, breathable clothing

🚨 **Seek immediate medical attention if:**
• Temperature above 103°F (39.4°C)
• Fever lasts more than 3 days
• Difficulty breathing or chest pain
• Severe headache or neck stiffness
• Persistent vomiting or dehydration signs

💡 **Prevention:** Get adequate rest, maintain good hygiene, and stay hydrated.

⚠️ This is general information. Consult a healthcare provider for persistent or high fever."""

        # Cold and flu symptoms
        elif any(word in message_lower for word in ['cold', 'flu', 'cough', 'runny nose', 'congestion', 'sore throat', 'sneezing']):
            return """**Cold & Flu Care:**

🤧 **Symptom Relief:**
• Rest and sleep 7-9 hours daily
• Drink warm liquids (tea, soup, warm water with honey)
• Use saline nasal rinses for congestion
• Gargle with warm salt water for sore throat
• Use humidifier or breathe steam from hot shower

💊 **Medications:**
• Pain relievers: acetaminophen or ibuprofen
• Decongestants for stuffy nose (short-term use)
• Throat lozenges for sore throat

🚨 **See a doctor if:**
• Symptoms worsen after 7-10 days
• High fever (>101.3°F/38.5°C)
• Difficulty breathing or wheezing
• Severe headache or sinus pain

⚠️ Antibiotics don't work for viral infections. Consult healthcare providers for proper diagnosis."""

        # Headache and pain
        elif any(word in message_lower for word in ['headache', 'head pain', 'migraine', 'pain', 'ache', 'hurt']):
            return """**Headache & Pain Relief:**

💊 **Immediate Relief:**
• Take over-the-counter pain relievers (acetaminophen, ibuprofen, aspirin)
• Apply cold compress to forehead or warm compress to neck
• Rest in a quiet, dark room
• Stay hydrated - drink plenty of water
• Gentle neck and shoulder massage

🧘 **Prevention & Management:**
• Maintain regular sleep schedule (7-9 hours)
• Manage stress through relaxation techniques
• Avoid known triggers (certain foods, bright lights)
• Regular exercise and healthy diet
• Limit screen time

🚨 **Emergency signs - seek immediate help:**
• Sudden, severe headache ("worst headache of life")
• Headache with fever, stiff neck, confusion
• Headache after head injury
• Vision changes or difficulty speaking
• Headache with weakness or numbness

⚠️ For chronic or recurring headaches, consult a healthcare provider for proper evaluation."""

        # Stomach and digestive issues
        elif any(word in message_lower for word in ['stomach', 'nausea', 'vomiting', 'diarrhea', 'constipation', 'indigestion', 'bloating']):
            return """**Digestive Health:**

🤢 **For Nausea/Vomiting:**
• Sip clear fluids slowly (water, ginger tea, clear broths)
• Eat bland foods (BRAT diet: bananas, rice, applesauce, toast)
• Avoid dairy, fatty, or spicy foods
• Rest and avoid strong odors

💩 **For Diarrhea:**
• Stay hydrated with oral rehydration solutions
• Eat binding foods (bananas, rice, toast)
• Avoid dairy, caffeine, and high-fiber foods temporarily
• Probiotics may help restore gut bacteria

🚫 **For Constipation:**
• Increase fiber intake (fruits, vegetables, whole grains)
• Drink plenty of water (8-10 glasses daily)
• Regular physical activity
• Establish regular bathroom routine

🚨 **Seek medical care if:**
• Severe dehydration signs
• Blood in vomit or stool
• Severe abdominal pain
• Symptoms persist >3 days

⚠️ Persistent digestive issues require medical evaluation."""

        # Skin conditions
        elif any(word in message_lower for word in ['rash', 'itchy', 'skin', 'allergy', 'hives', 'eczema', 'acne']):
            return """**Skin Care & Conditions:**

🧴 **General Skin Care:**
• Keep skin clean and moisturized
• Use gentle, fragrance-free products
• Avoid harsh scrubbing or hot water
• Protect from sun with SPF 30+ sunscreen
• Stay hydrated

🔴 **For Rashes/Irritation:**
• Apply cool, damp cloths to affected area
• Use over-the-counter hydrocortisone cream
• Take antihistamines for itching (Benadryl, Claritin)
• Avoid scratching to prevent infection
• Identify and avoid triggers

🌟 **For Acne:**
• Gentle cleansing twice daily
• Use non-comedogenic products
• Avoid picking or squeezing
• Consider over-the-counter treatments (benzoyl peroxide, salicylic acid)

🚨 **See a doctor if:**
• Rash spreads rapidly or covers large area
• Signs of infection (pus, red streaks, fever)
• Severe itching interfering with sleep
• Rash doesn't improve in 1-2 weeks

⚠️ Persistent or severe skin conditions need professional dermatological care."""

        # Sleep issues
        elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'fatigue', 'exhausted', 'sleepy']):
            return """**Sleep & Energy Management:**

😴 **Better Sleep Habits:**
• Maintain consistent sleep schedule (same bedtime/wake time)
• Create relaxing bedtime routine
• Keep bedroom cool, dark, and quiet
• Avoid screens 1 hour before bed
• Limit caffeine after 2 PM and alcohol before bed

⚡ **Combat Fatigue:**
• Get 7-9 hours of quality sleep
• Regular exercise (but not close to bedtime)
• Eat balanced meals and stay hydrated
• Take short naps (20-30 minutes) if needed
• Manage stress through relaxation techniques

🌙 **Sleep Hygiene Tips:**
• Use bedroom only for sleep and intimacy
• If can't sleep within 20 minutes, get up and do quiet activity
• Avoid large meals, spicy foods before bed
• Consider relaxation techniques (meditation, deep breathing)

🚨 **Consult a doctor if:**
• Chronic insomnia (>3 weeks)
• Excessive daytime sleepiness
• Loud snoring or breathing interruptions
• Persistent fatigue despite adequate sleep

⚠️ Sleep disorders require professional evaluation and treatment."""

        # Mental health and stress
        elif any(word in message_lower for word in ['stress', 'anxiety', 'depression', 'worried', 'sad', 'mental health', 'panic']):
            return """**Mental Health & Stress Management:**

🧠 **Stress Relief Techniques:**
• Deep breathing exercises (4-7-8 technique)
• Regular physical exercise
• Meditation or mindfulness practices
• Connect with friends and family
• Engage in hobbies you enjoy

💚 **Self-Care Strategies:**
• Maintain regular sleep schedule
• Eat nutritious, balanced meals
• Limit alcohol and avoid drugs
• Set realistic goals and priorities
• Practice gratitude and positive thinking

🤝 **When to Seek Help:**
• Persistent sadness or hopelessness
• Excessive worry interfering with daily life
• Panic attacks or severe anxiety
• Thoughts of self-harm
• Substance abuse as coping mechanism

📞 **Crisis Resources:**
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency services: 911

⚠️ Mental health is as important as physical health. Professional counseling and therapy can be very effective."""

        # Blood donation specific
        elif any(word in message_lower for word in ['blood', 'donate', 'donation', 'donor']):
            return """**Blood Donation Guidelines:**

🩸 **Eligibility Requirements:**
• Age 17-65 years (varies by location)
• Weight at least 110 lbs (50 kg)
• Good general health
• Hemoglobin levels within normal range
• No recent illness or infections

⏰ **Donation Frequency:**
• Whole blood: every 8-12 weeks
• Platelets: every 2 weeks (up to 24 times/year)
• Plasma: every 4 weeks

🥗 **Before Donation:**
• Eat iron-rich foods (spinach, red meat, beans)
• Stay well-hydrated
• Get good night's sleep
• Avoid alcohol 24 hours before
• Bring valid ID

🍪 **After Donation:**
• Rest for 10-15 minutes
• Drink plenty of fluids
• Eat snacks provided
• Avoid heavy lifting for 24 hours
• Keep bandage on for 4-6 hours

⚠️ Always follow guidelines from certified blood donation centers."""

        # Exercise and fitness
        elif any(word in message_lower for word in ['exercise', 'workout', 'fitness', 'muscle', 'weight loss', 'gym']):
            return """**Exercise & Fitness Guidelines:**

🏃 **Getting Started:**
• Start slowly and gradually increase intensity
• Aim for 150 minutes moderate exercise weekly
• Include both cardio and strength training
• Warm up before and cool down after exercise
• Listen to your body and rest when needed

💪 **Types of Exercise:**
• Cardio: walking, running, cycling, swimming
• Strength: weight lifting, resistance bands, bodyweight exercises
• Flexibility: yoga, stretching, tai chi
• Balance: yoga, pilates, balance exercises

🥗 **Nutrition for Fitness:**
• Eat balanced meals with protein, carbs, healthy fats
• Stay hydrated before, during, and after exercise
• Pre-workout: light snack 30-60 minutes before
• Post-workout: protein and carbs within 2 hours

⚠️ **Safety Tips:**
• Consult doctor before starting new exercise program
• Use proper form to prevent injury
• Wear appropriate gear and footwear
• Stop if you feel pain, dizziness, or shortness of breath

⚠️ Individual fitness needs vary. Consider consulting a fitness professional or healthcare provider."""

        # General health and wellness
        else:
            # Try to provide relevant response based on any health-related keywords
            health_keywords = ['health', 'wellness', 'medicine', 'doctor', 'hospital', 'treatment', 'symptoms', 'sick', 'illness']
            if any(keyword in message_lower for keyword in health_keywords):
                return f"""**General Health Information:**

Based on your question about "{message}", here are some general health guidelines:

🏥 **When to See a Healthcare Provider:**
• Persistent or worsening symptoms
• Symptoms interfering with daily activities
• Concerns about your health
• Preventive care and regular check-ups
• Medication management

🌟 **General Wellness Tips:**
• Maintain balanced diet with fruits, vegetables, whole grains
• Stay physically active (150 minutes/week moderate exercise)
• Get adequate sleep (7-9 hours nightly)
• Manage stress through healthy coping strategies
• Stay hydrated (8-10 glasses water daily)
• Avoid smoking and limit alcohol
• Practice good hygiene

📋 **Preventive Care:**
• Regular health screenings
• Vaccinations as recommended
• Dental and eye exams
• Monitor blood pressure and cholesterol
• Know your family medical history

🚨 **Emergency Warning Signs:**
• Chest pain or difficulty breathing
• Severe bleeding or trauma
• Loss of consciousness
• Severe allergic reactions
• Signs of stroke (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 911)

⚠️ This is general information only. For specific health concerns, always consult qualified healthcare professionals who can provide personalized medical advice based on your individual situation."""
            
            else:
                return f"""**Health Information Request:**

I understand you're asking about: "{message}"

While I can provide general health information on topics like:
• Common symptoms (fever, headache, cold, flu)
• Basic first aid and home remedies
• Wellness and prevention tips
• When to seek medical care
• Blood donation guidelines

**For your specific question, I recommend:**
• Consulting with a healthcare provider
• Calling a nurse hotline if available
• Visiting urgent care for non-emergency concerns
• Going to emergency room for serious symptoms

🚨 **Emergency situations - Call 911:**
• Difficulty breathing or chest pain
• Severe bleeding or trauma
• Loss of consciousness
• Signs of stroke or heart attack
• Severe allergic reactions

⚠️ This chatbot provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers for specific medical concerns."""
    
    def _get_fallback_response(self, message: str) -> str:
        return """I'm here to help with general health information. However, for specific medical concerns, I strongly recommend consulting with qualified healthcare professionals who can provide personalized advice based on your individual situation.

For medical emergencies, please contact emergency services immediately.

⚠️ This chatbot provides general information only and is not a substitute for professional medical advice, diagnosis, or treatment."""

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
    # Store user type in session to properly identify which table to query
    user_type = session.get('user_type')
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None
    
    if user_type == 'hospital':
        hospital = Hospital.query.get(user_id)
        if hospital:
            return hospital
    else:
        user = User.query.get(user_id)
        if user:
            return user
    
    return None

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

        # First, check if this email belongs to a hospital - always redirect hospitals to hospital login
        hospital = Hospital.query.filter_by(email=email).first()
        if hospital:
            flash('This account is registered as a hospital. Please use the Hospital Login.', 'warning')
            return redirect(url_for('hospital_login'))

        # Then, attempt to authenticate as a regular user (donor/patient)
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_type'] = 'user'
            login_user(user)
            return redirect(url_for('dashboard'))

        # Fallback invalid credentials
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
            session['user_type'] = 'hospital'
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
    donor_query = User.query.filter_by(role='user', is_verified_donor=True)
    if blood_group:
        donor_query = donor_query.filter(User.blood_group == blood_group)
    if city:
        donor_query = donor_query.filter(User.city.ilike(f'%{city}%'))
    if state:
        donor_query = donor_query.filter(User.state.ilike(f'%{state}%'))
    donors = donor_query.all()

    # Pending approvals logic: show donors with pending status that either
    # - explicitly selected this hospital by name, OR
    # - didn't specify a hospital name (so any hospital can review),
    # Optionally require an uploaded report; disabled to avoid empty list during testing.
    pending_query = User.query.filter(
        User.role == 'user',
        User.report_status == 'pending'
    )
    # Match by test_hospital_name if provided; allow nulls to be seen by all hospitals
    pending_query = pending_query.filter(
        or_(
            User.test_hospital_name.is_(None),
            User.test_hospital_name == '',
            User.test_hospital_name.ilike(f'%{current_user.name}%')
        )
    )
    pending_approvals = pending_query.all()
    
    # Get unique blood groups for filter dropdown (from verified donors only)
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

    # If no usage yet, render the form with an info banner that blood hasn't been used yet
    usage_exists = BloodUsage.query.filter_by(donor_id=donor.id, hospital_id=current_user.id).count() > 0
    return render_template('usage_form.html', donor=donor, usage_exists=usage_exists)

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

        # Match pending approvals logic used in hospital_dashboard
        pending_query = User.query.filter(
            User.role == 'user',
            User.report_status == 'pending'
        ).filter(
            or_(
                User.test_hospital_name.is_(None),
                User.test_hospital_name == '',
                User.test_hospital_name.ilike(f'%{current_user.name}%')
            )
        )
        pending_approvals = pending_query.count()

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