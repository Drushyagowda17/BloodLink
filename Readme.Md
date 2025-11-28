# BloodLink — Blood Donation Management System

BloodLink is a full-stack web application that connects blood donors with hospitals and medical facilities. It provides a secure and efficient platform for managing blood donations, finding donors during emergencies, and maintaining donor–hospital coordination.  
Built with **Flask**, **SQLite**, and modern web technologies.

---

## Features

### Donor Portal
- User registration and profile management (includes medical history)
- Dashboard with donation history and statistics
- Multi-language support: English, Kannada, Hindi
- Light/Dark theme support
- Privacy-first design — only verified hospitals can view donor data
- AI Medical Assistant for general health queries

### Hospital Portal
- Secure hospital registration using predefined hospital codes
- Donor search with filters (blood group, location, availability)
- Blood usage tracking and reporting
- Access to donor contact details (permission-based)
- Analytics dashboard

### System Features
- Responsive UI (mobile + tablet + desktop)
- Strong authentication and security (bcrypt hashing, Flask-Login)
- Internationalization support via JSON language files
- Real-time AI chatbot integration
- Print-friendly pages for donors and donor lists

---

## Technology Stack

**Backend:** Python 3.10+, Flask, SQLAlchemy  
**Database:** SQLite (auto-generated)  
**Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3  
**Icons:** Font Awesome 6  
**Authentication:** Flask-Login + bcrypt  
**Additional:** Custom internationalization system, browser-side theme switcher  

> Note: No `.env` file required. All configuration is inside `app.py`.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- PowerShell 7+ (optional for Windows)
- Virtual environment (recommended)

---

### 1. Clone the Repository
```bash
git clone https://github.com/Drushyagowda17/BloodLink.git
cd BloodLink
```

Or download the ZIP manually.

---

### 2. Install Dependencies

Using `requirements.txt`:
```bash
python -m pip install -r requirements.txt
```

Or install manually:
```bash
python -m pip install flask flask_sqlalchemy flask_bcrypt flask_login
```

---

### 3. Configuration (Optional)
You may edit these values inside `app.py`:

```python
SECRET_KEY = "your-secret-key"
HOSPITAL_CODES = "HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001"
CHATBOT_API_KEY = "your-api-key"   # Optional
```

> For production, move these variables into environment variables.

---

### 4. Start Fresh Database
Before first run:
```bash
rm instance/bloodlink.db
```

The app will auto-create a new database.

---

### 5. Run the Application
```bash
python app.py
```

Open:
```
http://localhost:5000
```

---

## Usage Guide

### Donor Workflow
1. Register at `/register`
2. Log in
3. Update your profile
4. View donation history and dashboard insights
5. Use AI assistant or switch themes/languages

### Hospital Workflow
1. Register at `/Hospital-Register` using a valid hospital code  
2. Log in at `/Hospital-Login`
3. Search donors by filters  
4. Record and track blood usage  
5. View/print donor lists  

---

## File Structure

```
BloodLink/
├── app.py                         # Main Flask application
├── bloodlink.db                   # SQLite database (auto-created)
├── requirements.txt               # Dependencies
├── static/
│   ├── css/
│   │   └── styles.css             # Custom styles + theming
│   ├── js/
│   │   └── scripts.js             # Client-side logic
│   └── i18n/                      # Language files
│       ├── en.json
│       ├── kn.json
│       └── hi.json
└── templates/
    ├── base.html
    ├── index.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── edit_profile.html
    ├── hospital_register.html
    ├── hospital_login.html
    ├── hospital_dashboard.html
    ├── usage_form.html
    └── error.html
```

---

## Configuration Details

### App Settings
- `SECRET_KEY` for sessions  
- `HOSPITAL_CODES` list for validation  
- Chatbot API key (optional)

### Database
- SQLite database is auto-generated  
- All tables created via SQLAlchemy  
- Stored locally as `bloodlink.db`

---

## Customization

### Themes
Edit CSS variables in:
```
static/css/styles.css
```

### Languages
Add new translation files under:
```
static/i18n/
```

### Hospital Codes
Modify inside `app.py`:
```python
HOSPITAL_CODES = "HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001"
```

---

## Security Highlights
- Password hashing using bcrypt with auto-generated salt  
- Flask-Login session protection  
- Role-based access (donor / hospital)  
- Input validation  
- Recommended: HTTPS in production  

---

## Browser Compatibility
 fully supports:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Android/iOS latest

Supports:
- ES6
- CSS Grid / Flexbox
- Local Storage

---

## Troubleshooting

### Database not created?
- Check file permissions  
- Ensure `instance/` folder is writable  

### Import errors?
```
pip list
```

### Port conflict?
```python
app.run(debug=True, port=5001)
```

### Chatbot not responding?
- Verify API key
- Ensure internet access

### Language not switching?
- Ensure `.json` files are valid  

---

## Contributing

1. Fork the repository  
2. Create a feature branch  
3. Commit changes  
4. Test thoroughly  
5. Open a pull request  

---

## License
Distributed under the **MIT License**.

---

## Support
Email: **drushyagmgowda@gmail.com**  
GitHub Issues: Create an issue in the repository  

---

## Changelog

### v1.0.0
- Initial release  
- Donor & hospital modules  
- AI Medical Assistant  
- Multi-language interface  
- Dark/Light theme  
- Responsive UI  

---

> Note: This is a college mini-project. Production deployments require stronger security, logging, backups, and complete validation.

