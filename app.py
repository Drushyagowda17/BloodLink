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
import requests # Added for API calls

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
            # Check for direct medical keywords first to use our custom safe responses
            # This ensures we prioritize our safe, verified answers over AI generation for critical topics
            if self._should_use_fallback(message):
                return self._get_medical_response(message)

            # Use free Hugging Face Inference API for general medical questions
            if self.provider == 'huggingface':
                return self._query_huggingface(message)
            elif self.provider == 'openai' and self.api_key:
                return self._query_openai(message)
            else:
                return self._get_medical_response(message)
        except Exception as e:
            print(f"Chatbot error: {e}")
            return self._get_medical_response(message)
    
    def _should_use_fallback(self, message: str) -> bool:
        # keywords that trigger our custom logic immediately
        # Added general health keywords: fever, cold, flu, headache, diet, sleep, stress, water
        keywords = ['blood', 'donate', 'donation', 'eligible', 'age', 'weight', 'height', 
                   'process', 'preparation', 'after', 'care', 'emergency', 'help', 'hello', 'hi',
                   'fever', 'cold', 'flu', 'headache', 'diet', 'nutrition', 'water', 'sleep', 'stress']
        return any(k in message.lower() for k in keywords)

    def _query_huggingface(self, message: str) -> str:
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
        """Generate comprehensive blood donation responses based on keywords"""
        message_lower = message.lower()

        # Check for user intent (Short vs Long answer)
        ask_why = any(w in message_lower for w in ['why', 'reason', 'cause', 'explain', 'detail', 'more info', 'how come'])
        
        # 0. Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening']):
            return "👋 Hello! I'm your BloodLink assistant. I can answer questions about blood donation eligibility, process, and safety. How can I help you today?"

        # 1. Emergency (Always Priority - No short version for safety)
        if any(word in message_lower for word in ['emergency', 'chest pain', 'breathing', 'bleeding', 'stroke', 'heart attack', 'call 100/108', 'unconscious', 'trauma']):
            return """🚨 **Emergency Warning Signs:**
• Chest pain or difficulty breathing
• Severe bleeding or trauma
• Loss of consciousness
• Severe allergic reactions
• Signs of stroke (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 100/108)

⚠️ **Call 100/108 immediately.** This information is for reference only."""

        # 2. Blood donation eligibility and age
        elif any(word in message_lower for word in ['age limit', 'how old', 'minimum age', 'maximum age', 'age requirement', 'age to donate']):
            if not ask_why:
                return """**Blood Donation Age Limits:**
• **Minimum:** 18 years old
• **Maximum:** 65 years old
• **Note:** First-time donors over 60 need doctor evaluation.
• **Regular donors:** Can continue past 65 if healthy."""
            else:
                return """**Blood Donation Age Requirements (Detailed):**

📋 **Eligibility Criteria:**
• Minimum age: 18 years old
• Maximum age: 65 years old (may vary by location)
• First-time donors over 60 may need additional evaluation

✅ **Why These Limits:**
• Under 18: Body still developing, blood volume may not be adequate
• Over 65: Increased health risks, slower recovery time
• Each donation removes about 450-500ml of blood

⚕️ **Age-Related Considerations:**
• 18-24: Ideal age group, quick recovery
• 25-45: Prime donation years
• 46-60: Regular health check-ups recommended
• 60+: Doctor's approval often required

⚠️ Always consult with blood bank staff about age-specific requirements in your region."""

        # 3. When can I donate blood / frequency
        elif any(word in message_lower for word in ['when can i donate', 'how often', 'frequency', 'how many times', 'donation interval', 'again']):
            if not ask_why:
                return """**Donation Frequency:**
• **Whole Blood (Men):** Every 3 months
• **Whole Blood (Women):** Every 4 months
• **Platelets:** Every 2 weeks
• **Plasma:** Every 4 weeks"""
            else:
                return """**Blood Donation Frequency (Detailed):**

🩸 **Whole Blood Donation:**
• Men: Every 3 months (12 weeks)
• Women: Every 4 months (16 weeks)
• Minimum 8-12 weeks between donations

🔄 **Other Donation Types:**
• Platelets: Every 2 weeks (up to 24 times/year)
• Plasma: Every 4 weeks
• Double Red Cells: Every 6 months

⏰ **Why Wait Between Donations:**
• Body needs time to replenish blood cells
• Iron levels must return to normal
• Hemoglobin restoration takes time
• Prevents anemia and fatigue

📅 **Recovery Timeline:**
• 24 hours: Plasma volume restored
• 2 weeks: Red blood cells increase
• 8 weeks: Full blood volume restored

⚠️ Always check with your local blood bank for specific guidelines."""

        # 4. Blood donation preparation / before donating
        elif any(word in message_lower for word in ['before donating', 'preparation', 'prepare', 'what to do before', 'eat before', 'drink before']):
            if not ask_why:
                return """**Before Donating:**
• **Eat:** Iron-rich foods and a healthy meal 2-3 hours before.
• **Drink:** 16 oz of water.
• **Avoid:** Fatty foods, alcohol (24h), and smoking (1h).
• **Bring:** ID and medication list."""
            else:
                return """**Blood Donation Preparation (Detailed):**

🥗 **24 Hours Before:**
• Eat iron-rich foods (spinach, red meat, beans, fortified cereals)
• Stay well-hydrated (8-10 glasses of water)
• Get adequate sleep (7-8 hours)
• Avoid alcohol consumption

🍽️ **Day of Donation:**
• Eat a healthy meal 2-3 hours before
• Include protein and complex carbohydrates
• Drink extra fluids (16 oz water 2 hours before)
• Avoid fatty foods (delays testing)

☕ **What to Avoid:**
• Fatty or greasy foods (affects blood quality)
• Alcohol (24 hours before)
• Aspirin (48 hours before - for platelet donation)
• Smoking (1 hour before and after)

✅ **What to Bring:**
• Valid photo ID
• List of current medications
• Blood bank donor card
• Emergency contact information

⚠️ Following these guidelines ensures a safe, comfortable donation experience."""

        # 5. After blood donation / post-donation care
        elif any(word in message_lower for word in ['after donation', 'after donating', 'post donation', 'recovery', 'what to do after']):
            if not ask_why:
                return """**After Care:**
• **Immediate:** Rest 15 mins, eat snacks, keep bandage on 4h.
• **Next 24h:** Drink extra fluids, avoid heavy lifting/exercise.
• **Diet:** Eat iron-rich foods (meat, spinach)."""
            else:
                return """**After Blood Donation Care (Detailed):**

⏱️ **Immediate Care (First 30 Minutes):**
• Rest for 10-15 minutes in observation area
• Eat snacks and drink fluids provided
• Keep bandage on for 4-6 hours
• Avoid sudden movements

🥤 **First 24 Hours:**
• Drink extra fluids (8-10 glasses of water)
• Avoid alcohol for 24 hours
• No heavy lifting or strenuous exercise
• No hot baths or saunas
• Keep donation site clean and dry

🚫 **Activities to Avoid:**
• Heavy lifting (24 hours)
• Vigorous exercise (24 hours)
• Swimming (24 hours)
• Operating heavy machinery (if feeling dizzy)

⚠️ **Warning Signs - Contact Doctor If:**
• Continued bleeding from puncture site
• Severe bruising or swelling
• Persistent dizziness or fainting
• Signs of infection

✅ Most people feel normal within a few hours."""

        # 6. Blood types and compatibility
        elif any(word in message_lower for word in ['blood type', 'blood group', 'compatibility', 'universal donor', 'universal recipient', 'o negative', 'ab positive']):
            if not ask_why:
                return """**Blood Types:**
• **Universal Donor:** O Negative (O-)
• **Universal Recipient:** AB Positive (AB+)
• **Most Common:** O Positive (O+)
• **Rarest:** AB Negative (AB-)"""
            else:
                return """**Blood Types and Compatibility (Detailed):**

🩸 **The 8 Blood Types:**
1. O Positive (O+) - Most common
2. O Negative (O-) - Universal donor
3. A Positive (A+)
4. A Negative (A-)
5. B Positive (B+)
6. B Negative (B-)
7. AB Positive (AB+) - Universal recipient
8. AB Negative (AB-) - Rarest

🎯 **Universal Roles:**
• **O Negative:** Can donate red cells to ANYONE.
• **AB Positive:** Can receive red cells from ANYONE.

📊 **Who Can Donate to Whom:**
• **O-**: Everyone
• **O+**: O+, A+, B+, AB+
• **A-**: A-, A+, AB-, AB+
• **A+**: A+, AB+
• **B-**: B-, B+, AB-, AB+
• **B+**: B+, AB+
• **AB-**: AB-, AB+
• **AB+**: AB+ only

🔬 **Why Blood Types Matter:**
• Antibodies attack incompatible blood cells.
• Matching prevents serious reactions.

⚠️ Always inform medical staff of your blood type."""

        # 7. Benefits of donating blood
        elif any(word in message_lower for word in ['benefits', 'why donate', 'advantage', 'good for health', 'why should i']):
            if not ask_why:
                return """**Benefits:**
• Saves up to 3 lives.
• Free health screening (BP, Hemoglobin).
• Reduces risk of heart disease.
• Burns ~650 calories.
• Psychological satisfaction."""
            else:
                return """**Benefits of Blood Donation (Detailed):**

❤️ **Health Benefits for Donors:**
1. **Heart Health:** Reduces blood viscosity and iron overload, lowering heart disease risk.
2. **Free Health Screening:** Checks blood pressure, hemoglobin, and screens for diseases.
3. **Calorie Burn:** Burns ~650 calories per donation; body works to replenish blood.
4. **Cancer Risk:** May reduce risk by lowering oxidative stress.
5. **Cell Production:** Stimulates production of new blood cells.

🌟 **Social Benefits:**
• Save up to 3 lives per donation (Red cells, Plasma, Platelets)
• Support emergency and trauma patients
• Contribute to community health
• Sense of purpose and fulfillment

⚠️ One donation can make a massive difference."""

        # 8. Who cannot donate blood / disqualifications
        elif any(word in message_lower for word in ['cannot donate', 'disqualified', 'not eligible', 'who cannot', 'restrictions', 'banned']):
            if not ask_why:
                return """**Disqualifications:**
• **Permanent:** HIV/AIDS, Hepatitis B/C.
• **Temporary:** Cold/Flu (2 weeks), Antibiotics (1 week), Tattoo (3-12 months), Pregnancy (wait 6 months post-birth), Recent Malaria travel."""
            else:
                return """**Blood Donation Disqualifications (Detailed):**

🚫 **Permanent Disqualifications:**
• HIV/AIDS positive
• Hepatitis B or C (current infection)
• Certain cancers (leukemia, lymphoma)
• High-risk sexual behavior
• Injectable drug use

⏳ **Temporary Disqualifications:**
• **Illness:** Cold/Flu (Wait 2 weeks after recovery)
• **Medication:** Antibiotics (Wait until course finished)
• **Pregnancy:** Cannot donate. Wait 6 months after childbirth.
• **Tattoo/Piercing:** Wait 3 months to 1 year.
• **Travel:** Malaria-risk areas (Wait 3 months to 3 years).
• **Surgery:** Wait 6-12 months.

⚖️ **Health Requirements:**
• Must weigh at least 50 kg (110 lbs).
• Must have adequate hemoglobin levels.

⚠️ Guidelines vary by country. Temporary deferral doesn't mean a permanent ban."""

        # 9. Blood donation process / procedure
        elif any(word in message_lower for word in ['process', 'procedure', 'how to donate', 'what happens', 'steps', 'donation process']):
            if not ask_why:
                return """**Process (45-60 mins):**
1. **Registration:** ID check & forms.
2. **Screening:** BP, temp, and iron check.
3. **Donation:** 8-10 mins for whole blood.
4. **Recovery:** Rest 15 mins with snacks."""
            else:
                return """**Blood Donation Process (Detailed):**

📋 **Step-by-Step:**

**1. Registration (10 min):**
• ID check, medical history form, and consent.

**2. Health Screening (15 min):**
• Vitals check (Temp, BP, Pulse).
• Finger prick for hemoglobin/iron level.
• Private interview about health history.

**3. The Donation (10 min):**
• Sterile needle insertion (slight pinch).
• Collects ~450ml (1 pint).
• Staff monitors you throughout.

**4. Recovery (15 min):**
• Bandage applied.
• Rest in observation area.
• Snacks and juice provided to restore energy.

✅ **Safety:**
• Single-use sterile needles are used.
• You cannot get infections from donating.

⚠️ The actual blood draw only takes about 10 minutes."""

        # 10. Pain during donation
        elif any(word in message_lower for word in ['hurt', 'pain', 'painful', 'does it hurt', 'needle pain']):
            return """**Does it Hurt?**
• **Sensation:** A quick pinch (2-3 seconds) when the needle goes in.
• **During:** You shouldn't feel pain while blood flows.
• **Comparison:** Less painful than a dental visit; similar to a vaccine.
• **Tip:** Look away and take a deep breath to relax."""

        # 11. Dizziness or fainting
        elif any(word in message_lower for word in ['dizzy', 'faint', 'lightheaded', 'feel weak', 'pass out']):
            if not ask_why:
                return """**Dizziness:**
• **Prevention:** Eat a big meal & drink water before.
• **If Dizzy:** Lie down immediately, raise legs, drink fluids.
• **Commonality:** Affects <5% of donors."""
            else:
                return """**Dizziness & Fainting (Detailed):**

😵 **Why It Happens:**
• Temporary drop in blood pressure.
• Nervousness or empty stomach.
• Dehydration.

✅ **Prevention:**
• **Hydrate:** 16oz water before donating.
• **Eat:** A full meal 2-3 hours prior.
• **Relax:** Don't watch the needle.

💊 **If You Feel Dizzy:**
• Tell staff immediately.
• Lie down or put head between knees.
• Do not try to walk or drive.

⚠️ **After Care:**
• Rest for 30 mins.
• Avoid hot showers or rushing.
• Most dizziness passes quickly."""

        # 12. Weight requirements
        elif any(word in message_lower for word in ['weight', 'how much', 'minimum weight', 'underweight', 'overweight']):
            return """**Weight Requirements:**
• **Minimum:** 50 kg (110 lbs).
• **Why:** Safety. Donating too much blood volume for your body size can be dangerous.
• **Underweight:** Cannot donate for your safety.
• **Overweight:** No upper limit as long as you are healthy."""

        # 13. Hemoglobin requirements
        elif any(word in message_lower for word in ['hemoglobin', 'haemoglobin', 'iron', 'anemia', 'anaemia', 'low hemoglobin']):
            if not ask_why:
                return """**Iron/Hemoglobin:**
• **Men:** Min 13.0 g/dL
• **Women:** Min 12.0 g/dL
• **Low Iron?** Eat red meat, spinach, fortified cereals with Vitamin C.
• **Deferral:** Temporary until levels return to normal."""
            else:
                return """**Hemoglobin & Iron Requirements (Detailed):**

🔬 **Minimum Levels:**
• **Men:** 13.0 g/dL
• **Women:** 12.0 g/dL

❌ **Low Hemoglobin:**
• You will be temporarily deferred (not banned).
• Ensures you don't become anemic.

✅ **How to Increase Iron:**
• **Heme Iron (Best):** Red meat, organ meats, poultry, fish.
• **Non-Heme Iron:** Spinach, beans, lentils, tofu, fortified cereals.
• **Booster:** Eat iron foods with Vitamin C (oranges, tomatoes) to absorb more.
• **Blocker:** Avoid tea/coffee with meals (blocks absorption).

⚠️ Consult a doctor if your iron is persistently low."""

        # 14. Common Cold/Flu
        elif any(word in message_lower for word in ['cold', 'flu', 'cough', 'sneeze', 'runny nose']):
             return """**Common Cold & Flu Tips:**
• **Rest:** Your body needs energy to fight the virus.
• **Hydrate:** Drink plenty of water, herbal tea, or soup.
• **Symptom Relief:** Over-the-counter meds can help (consult a pharmacist).
• **Prevention:** Wash hands frequently.
⚠️ See a doctor if symptoms last >10 days or high fever persists."""

        # 15. Fever
        elif any(word in message_lower for word in ['fever', 'temperature', 'high temp']):
            return """**Fever Management:**
• **Adults:** Fever is usually >100.4°F (38°C).
• **Care:** Rest, drink fluids, stay cool.
• **Medication:** Acetaminophen or ibuprofen can lower fever.
• **Warning:** Seek help if fever is >103°F (39.4°C) or lasts >3 days."""

        # 16. Headache
        elif any(word in message_lower for word in ['headache', 'migraine', 'head pain']):
            return """**Headache Relief:**
• **Hydration:** Dehydration is a common cause. Drink water.
• **Rest:** Lie down in a dark, quiet room.
• **Tension:** Massage neck/temples or use a warm compress.
• **Screen Time:** Take breaks from phones/computers.
⚠️ Seek immediate help for "worst headache of your life" or sudden severe pain."""

        # 17. Hydration/Water
        elif any(word in message_lower for word in ['water', 'hydrate', 'hydration', 'drink']):
            return """**Hydration Basics:**
• **Daily Goal:** About 8 glasses (2 liters) per day, more if active.
• **Benefits:** Energy, skin health, digestion, headache prevention.
• **Signs of Dehydration:** Thirst, dark urine, fatigue, dizziness."""

        # 18. Sleep
        elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'rest']):
             return """**Healthy Sleep Habits:**
• **Duration:** Adults need 7-9 hours per night.
• **Routine:** Go to bed at the same time daily.
• **Environment:** Keep room dark, cool, and quiet.
• **Avoid:** Caffeine and screens before bed."""

        # Fallback response for unrecognized queries
        else:
            return f"""**Health Information Request:**

I understand you're asking about: "{message}"

I can help with:
• **Eligibility:** Age, weight, rules.
• **Process:** How to donate, pain, time.
• **Health:** Iron levels, side effects.
• **Common Issues:** Fever, Cold, Sleep.
• **Preparation:** What to eat/drink.

For specific medical advice or emergencies, please consult a doctor.

🚨 **Call 100/108for emergencies.**"""

    def _get_fallback_response(self, message: str) -> str:
        return """I'm here to help with general blood donation info. For specific medical concerns, please consult a doctor.

For medical emergencies, please contact emergency services immediately.

⚠️ This chatbot provides general information only."""

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

    # Pending approvals logic
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
