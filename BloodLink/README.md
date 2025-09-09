# BloodLink — Blood Donation Management System

BloodLink is a web application that connects blood donors with hospitals and medical facilities. Built with **Flask**, **SQLite**, and modern web technologies, it provides a secure, friendly platform for managing blood donations and finding donors during emergencies.

---

## Features

### For Donors
- **User Registration & Profile Management** – Complete donor profiles with medical history  
- **Dashboard** – View donation history and basic statistics  
- **Privacy Protection** – Personal data visible only to verified hospitals  
- **Medical Assistant** – AI-powered chatbot for general health information  
- **Multi-language Support** – English, Kannada, and Hindi  
- **Dark/Light Theme** – Customizable interface themes  

### For Hospitals
- **Hospital Registration** – Secure onboarding with hospital codes  
- **Donor Search** – Filter by blood type, location, and availability  
- **Usage Tracking** – Record and manage blood usage history  
- **Contact Management** – Direct access to donor contact information  
- **Dashboard Analytics** – View statistics and manage records  

### Technical Features
- **Responsive Design** – Works on desktop, tablet, and mobile  
- **Security** – Password hashing, session management, and data protection  
- **Accessibility** – WCAG-aware design with keyboard navigation  
- **Internationalization** – Easy to add new languages  
- **Real-time Chat** – Medical assistant chatbot integration  
- **Print Support** – Printable profiles and donor lists  

---

## Technology Stack
- **Backend**: Python 3.10+, Flask, SQLAlchemy  
- **Database**: SQLite (auto-created)  
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)  
- **UI Framework**: Bootstrap 5.3  
- **Icons**: Font Awesome 6.0  
- **Authentication**: Flask-Login with bcrypt password hashing  

> **Note:** This setup does **not** require a `.env` file. Configuration can be edited directly in code (e.g., `app.py`).

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher  
- PowerShell 7.0+ on Windows (optional)  
- Virtual environment is optional  

### 1) Clone or Download
```bash
# Using git
git clone https://github.com/Drushyagowda17/BloodLink.git
cd BloodLink

# Or download the ZIP from GitHub and extract it
2) Install All Dependencies
Run this in your terminal (installs everything at once):

bash
Copy code
python -m pip install flask flask_sqlalchemy flask_bcrypt flask_login flask_wtf email_validator
Or create a requirements.txt with:

txt
Copy code
flask
flask_sqlalchemy
flask_bcrypt
flask_login
flask_wtf
email_validator
and install via:

bash
Copy code
python -m pip install -r requirements.txt
3) Run the Application
bash
Copy code
python app.py
Visit: http://localhost:5000

Usage Guide
First-Time Setup
Start the application

The SQLite database (bloodlink.db) will be created automatically

Open http://localhost:5000 in your browser

Donors
Register at /register

Login with your email and password

Manage Profile from your dashboard

View History and basic statistics

Hospitals
Register at /Hospital-Register using a valid hospital code

Login at /Hospital-Login

Search Donors using filters (blood type, location, availability)

Record Usage by creating usage records when blood is used

File Structure
php
Copy code
BloodLink/
├── app.py                      # Main Flask application
├── bloodlink.db                # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── static/
│   ├── css/
│   │   └── styles.css          # Custom styles with theme support
│   ├── js/
│   │   └── scripts.js          # JavaScript functionality
│   └── i18n/
│       ├── en.json             # English translations
│       ├── kn.json             # Kannada translations
│       └── hi.json             # Hindi translations
└── templates/
    ├── base.html               # Base template with navigation
    ├── index.html              # Landing page
    ├── register.html           # Donor registration
    ├── login.html              # Donor login
    ├── dashboard.html          # Donor dashboard
    ├── edit_profile.html       # Profile editing
    ├── hospital_register.html  # Hospital registration
    ├── hospital_login.html     # Hospital login
    ├── hospital_dashboard.html # Hospital dashboard
    ├── usage_form.html         # Blood usage recording
    └── error.html              # Error pages
Configuration
Application Settings (in code)
SECRET_KEY – Flask secret key for sessions

HOSPITAL_CODES – Comma-separated list of valid hospital codes

Chatbot provider/API key – if the medical assistant feature is enabled

Database
SQLite database is created automatically on first run

No migrations required – tables are created using SQLAlchemy

Database file: bloodlink.db

Troubleshooting
Database not created

Ensure Python has write permissions in the project directory

Confirm bloodlink.db appears after first run

Import errors

Verify dependencies are installed (pip list)

Port already in use

Change the port in app.py: app.run(debug=True, port=5001)

License
This project is licensed under the MIT License. See the LICENSE file for details.

Support
Email: drushyagmgowda@gmail.com

Issues: Open an issue on GitHub

Note: This is a college mini-project built for educational and demonstration purposes. For production use, add rigorous security, proper API integrations, logging, and comprehensive testing.
