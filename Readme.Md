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
- Blood test report upload and verification tracking

### Hospital Portal
- Secure hospital registration using predefined hospital codes
- Donor search with filters (blood group, location, availability)
- **Donor Verification System** - Approve/Reject donors with blood test review
- Blood usage tracking and reporting
- Access to donor contact details (permission-based)
- Analytics dashboard
- Collapsible blood usage history
- Data export to CSV

### System Features
- Responsive UI (mobile + tablet + desktop)
- Strong authentication and security (bcrypt hashing, Flask-Login)
- Internationalization support via JSON language files
- Real-time AI chatbot integration
- Print-friendly pages for donors and donor lists
- Dark mode support with smooth transitions
- Keyboard shortcuts and accessibility features

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
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git (optional, for cloning)

---

### 1. Clone or Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/Drushyagowda17/BloodLink-Blood-Donation-Management-System.git
cd BloodLink-Blood-Donation-Management-System
```

**Option B: Manual Download**
- Download the ZIP file
- Extract it
- Open terminal/PowerShell in the extracted folder

---

### 2. Create a Virtual Environment

A virtual environment isolates project dependencies from your system Python.

#### **On Windows (PowerShell or CMD):**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For PowerShell:
.\venv\Scripts\Activate.ps1

# For Command Prompt (CMD):
venv\Scripts\activate.bat
```

**Note:** If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **On macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**You should see `(venv)` at the beginning of your terminal prompt when activated.**

---

### 3. Verify Virtual Environment is Active

```bash
# Check Python location (should be in venv folder)
which python          # macOS/Linux
where python          # Windows

# Check pip location
which pip             # macOS/Linux
where pip             # Windows
```

---

### 4. Install Dependencies

With virtual environment activated:

```bash
# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Or install manually:**
```bash
pip install flask flask_sqlalchemy flask_bcrypt flask_login python-dotenv requests
```

**Verify installation:**
```bash
pip list
```

---

### 5. Configuration (Optional)

You may edit these values inside `app.py`:

```python
SECRET_KEY = "your-secret-key"
HOSPITAL_CODES = "HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001"
CHATBOT_API_KEY = "your-api-key"   # Optional
```

> For production, move these variables into environment variables.

---

### 6. Clear/Reset Database

#### **Option A: Delete Database File (Fresh Start)**

If you want to start with a completely fresh database:

```bash
# On Windows (PowerShell):
Remove-Item -Path "instance\bloodlink.db" -Force

# On Windows (CMD):
del instance\bloodlink.db

# On macOS/Linux:
rm instance/bloodlink.db
( THIS SHOULD GIVE AN ERROR WHEN YOU RUN IT "BloodLink-Blood-Donation-Management-System\instance\bloodlink.db' because it does not exist" JUST A PRE-CAUTION)
---

### 7. Run the Application

With virtual environment activated:

```bash
python app.py
```

**Output should show:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Open in browser:**
```
http://localhost:5000
```

---

### 8. Deactivate Virtual Environment (When Done)

```bash
# On Windows, macOS, and Linux:
deactivate
```

---


## Usage Guide

### Donor Workflow
1. Register at `/register` with blood test report
2. Log in at `/login`
3. Update your profile at `/profile/edit`
4. View donation history and dashboard insights
5. Check verification status
6. Use AI assistant or switch themes/languages

### Hospital Workflow
1. Register at `/Hospital-Register` using a valid hospital code  
2. Log in at `/Hospital-Login`
3. View pending donor approvals
4. Review blood test reports
5. Approve or reject donors
6. Search verified donors by filters  
7. Record and track blood usage  
8. View/print donor lists  
9. Export data to CSV

---

## File Structure

```
BloodLink/
├── app.py                         # Main Flask application
├── requirements.txt               # Dependencies
├── Readme.Md                      # This file
├── instance/
│   └── bloodlink.db               # SQLite database (auto-created)
├── static/
│   ├���─ css/
│   │   └── styles.css             # Custom styles + theming
│   ├── js/
│   │   └── scripts.js             # Client-side logic
│   ├── uploads/                   # Blood test report uploads
│   └── i18n/                      # Language files
│       ├── en.json
│       ├── kn.json
│       └── hi.json
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── edit_profile.html
│   ├── hospital_register.html
│   ├── hospital_login.html
│   ├── hospital_dashboard.html   
│   ├── usage_form.html            
│   └── error.html

```

---

## Configuration Details

### App Settings
- `SECRET_KEY` for sessions  
- `HOSPITAL_CODES` list for validation  
- Chatbot API key (optional)

### Database
- SQLite database is auto-generated in `instance/` folder
- All tables created via SQLAlchemy  
- Stored locally as `bloodlink.db`

### Virtual Environment
- Isolates project dependencies
- Prevents conflicts with system Python
- Easy to delete and recreate

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
- File upload restrictions
- CSRF protection
- Recommended: HTTPS in production  

---

## Browser Compatibility

Fully supports:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Android/iOS latest

Supports:
- ES6
- CSS Grid / Flexbox
- Local Storage
- Service Workers

---

## Troubleshooting

### Virtual Environment Issues

**Q: Virtual environment not activating?**
```bash
# Windows PowerShell - Check execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

**Q: "python: command not found"?**
```bash
# Make sure Python is installed
python --version

# Or try python3
python3 --version
```

**Q: Modules not found after activation?**
```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Database Issues

**Q: Database not created?**
```bash
# Check if instance folder exists
ls instance/          # macOS/Linux
dir instance          # Windows

# If not, create it
mkdir instance        # macOS/Linux
md instance           # Windows
```

**Q: "database is locked" error?**
```bash
# Close all instances of the app
# Then delete the database and restart
rm instance/bloodlink.db
python app.py
```

**Q: Want to clear all data?**
```bash
#Delete database file
rm instance/bloodlink.db


```

### Application Issues

**Q: Import errors?**
```bash
pip list
pip install -r requirements.txt
```

**Q: Port conflict (5000 already in use)?**
```python
# Edit app.py, change port:
app.run(debug=True, port=5001)
```

**Q: Chatbot not responding?**
- Verify API key in `app.py`
- Ensure internet access
- Check browser console for errors

**Q: Language not switching?**
- Ensure `.json` files are valid  
- Check browser console for errors
- Clear browser cache

**Q: Dark mode not working?**
- Clear browser cache
- Try different browser
- Check if CSS is loaded

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

### v2.0.0 (Latest)
- ✅ Hospital dashboard redesign
- ✅ Donor verification system
- ✅ Blood usage recording with confirmation
- ✅ Enhanced visibility in light and dark modes
- ✅ Full dark mode support
- ✅ Responsive design improvements
- ✅ Data export to CSV
- ✅ Collapsible blood usage history
- ✅ Comprehensive documentation

### v1.0.0
- Initial release  
- Donor & hospital modules  
- AI Medical Assistant  
- Multi-language interface  
- Dark/Light theme  
- Responsive UI  

---

## Quick Start Commands

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt


# 4. Run application
python app.py

# 5. Open browser
# http://localhost:5000


```

---

## Important Notes

⚠️ **Before First Run:**
- Create virtual environment
- Install dependencies
- Database will auto-create on first run

⚠️ **Database Updates:**
- If you see database errors, clear the database
- delete `rm instance/bloodlink.db`
- App will recreate database automatically

⚠️ **Production Deployment:**
- This is a college mini-project
- For production, implement:
  - Stronger security measures
  - Comprehensive logging
  - Database backups
  - Complete input validation
  - HTTPS/SSL
  - Environment variables for secrets

---

> **Last Updated:** 2025  
> **Version:** 2.0  
> **Status:** Production Ready
