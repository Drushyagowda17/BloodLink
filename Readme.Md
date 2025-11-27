# BloodLink — Blood Donation Management System

BloodLink is a web application that connects blood donors with hospitals and medical facilities. Built with *Flask, **SQLite*, and modern web technologies, it provides a secure, friendly platform for managing blood donations and finding donors during emergencies.

---

## 🚀 Features

### 👤 For Donors
- *User Registration & Profile Management* (medical history included)  
- *Dashboard* with donation history & basic statistics  
- *Privacy Protection* — only verified hospitals can view data  
- *AI Medical Assistant* for general health queries  
- *Multi-Language Support* – English, Kannada, Hindi  
- *Dark/Light Theme* switch  

### 🏥 For Hospitals
- *Hospital Registration* using secure hospital codes  
- *Donor Search* – filter by blood group, location, availability  
- *Usage Tracking* – record and manage blood usage  
- *Contact Management* – view donor info  
- *Dashboard Analytics*  

### ⚙ Technical Features
- Responsive UI (mobile/tablet/desktop)  
- Strong security (bcrypt, sessions, RBAC)  
- Accessible design (WCAG principles)  
- Internationalization system  
- Real-time chatbot integration  
- Print support for profiles & donor lists  

---

## 🛠 Technology Stack

- *Backend:* Python 3.10+, Flask, SQLAlchemy  
- *Database:* SQLite (auto-created)  
- *Frontend:* HTML5, CSS3, JavaScript (ES6+)  
- *Frameworks:* Bootstrap 5.3  
- *Icons:* Font Awesome 6  
- *Auth:* Flask-Login + bcrypt hashing  

> *Note:* No .env file required. All configuration is inside app.py.

---

## 📥 Installation & Setup

### ✔ Prerequisites
- Python 3.10+  
- PowerShell 7+ (Windows, optional)  
- Virtual environment (optional)

---

### 1️⃣ Clone or Download

```bash
git clone https://github.com/Drushyagowda17/BloodLink.git
cd BloodLink
Or download the Zip manually 

⿢ Install Dependencies

Using requirements.txt:

python -m pip install -r requirements.txt

Or manually:

python -m pip install flask flask_sqlalchemy flask_bcrypt flask_login

⿣ Configuration (Optional)
Edit these in app.py if needed:
SECRET_KEY
HOSPITAL_CODES = 'HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001'
Chatbot API key (optional)
> Production deployments should move these to environment variables.

❗ IMPORTANT — Start Fresh Database

Before first run:
rm instance/bloodlink.db

⿤ Run the Application

python app.py
Then open:
http://localhost:5000

📚 Usage Guide

🔰 First-Time Setup
1. Run the app
2. Database auto-creates
3. Open browser
4. Register as donor/hospital

👤 Donor Workflow

Register at /register
Login
Update profile
Access dashboard, see donation history


🏥 Hospital Workflow

Register at /Hospital-Register using a valid code
Login at /Hospital-Login
Search donors with filters
Record blood usage
Manage donor interactions
🗂 File Structure

BloodLink/
├── app.py                      # Main Flask app
├── bloodlink.db                # SQLite database (auto-created)
├── requirements.txt            # Dependency list
├── README.md                   # Project documentation
├── static/
│   ├── css/
│   │   └── styles.css          # Custom stylesheet & themes
│   ├── js/
│   │   └── scripts.js          # Client-side behavior
│   └── i18n/
│       ├── en.json             # English language file
│       ├── kn.json             # Kannada language file
│       └── hi.json             # Hindi language file
└── templates/
    ├── base.html               # Layout template
    ├── index.html              # Homepage
    ├── register.html           # Donor registration
    ├── login.html              # Donor login
    ├── dashboard.html          # Donor dashboard
    ├── edit_profile.html       # Edit profile page
    ├── hospital_register.html  # Hospital registration
    ├── hospital_login.html     # Hospital login
    ├── hospital_dashboard.html # Hospital dashboard
    ├── usage_form.html         # Blood usage record form
    └── error.html              # Error templates


⚙ Configuration

App Settings (inside app.py)
SECRET_KEY – session security
HOSPITAL_CODES – HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001
Chatbot API key (optional)

Database Behavior

SQLite database autogenerates
All tables created by SQLAlchemy
Stored as bloodlink.db

🎨 Customization

Theme

Edit CSS variables in:
static/css/styles.css
Add Languages
Add new JSON translation files in:
static/i18n/
Update Hospital Codes

Modify:

HOSPITAL_CODES = "HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001"

inside app.py.

🔐 Security Features

Hashed passwords (bcrypt with salt)
Flask-Login session security
Access-level control (donor/hospital)
Input validation
CSRF-safe patterns
HTTPS recommended for deployment

🌐 Browser Support

Chrome 90+
Firefox 88+
Safari 14+
Edge 90+
Mobile (Android/iOS latest)

Supports:

ES6
CSS Grid
Flexbox
Local Storage

🛠 Troubleshooting

Database not created?
Ensure Python has write permissions
Check if bloodlink.db appears
Import errors?
pip list
Port already in use?
Modify:

app.run(debug=True, port=5001)
Chatbot not working?
Check API key
Ensure stable internet
Language Not Loading?
Ensure *.json files exist and are valid

🤝 Contributing

1. Fork repository
2. Create new branch
3. Commit changes
4. Test fully
5. Create Pull Request

📄 License

MIT License — free to use, modify, and distribute.

📬 Support

Email: drushyagmgowda@gmail.com
Issues: Create one in GitHub Issues

📝 Changelog

v1.0.0
Initial Release
Donor & Hospital Management
Multi-language support
Responsive UI
Medical Assistant Chatbot
Dark/Light Theme

> ⚠ Note: This is a college mini-project. For production: add robust security, API integrations, logging, backups, and thorough testing.
