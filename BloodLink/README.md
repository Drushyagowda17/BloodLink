# BloodLink - Blood Donation Management System

BloodLink is a comprehensive web application that connects blood donors with hospitals and medical facilities. Built with Flask, SQLite, and modern web technologies, it provides a secure and user-friendly platform for managing blood donations and finding donors during emergencies.

## Features

### For Donors
- **User Registration & Profile Management**: Complete donor profiles with medical history
- **Dashboard**: View donation history and statistics
- **Privacy Protection**: Personal data visible only to verified hospitals
- **Medical Assistant**: AI-powered chatbot for health information
- **Multi-language Support**: English, Kannada, and Hindi
- **Dark/Light Theme**: Customizable interface themes

### For Hospitals
- **Hospital Registration**: Secure registration with hospital codes
- **Donor Search**: Advanced filtering by blood type, location, and availability
- **Usage Tracking**: Record and manage blood usage history
- **Contact Management**: Direct access to donor contact information
- **Dashboard Analytics**: View statistics and manage records

### Technical Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Security**: Password hashing, session management, and data protection
- **Accessibility**: WCAG compliant with keyboard navigation support
- **Internationalization**: Multi-language support with easy translation
- **Real-time Chat**: Medical assistant chatbot integration
- **Print Support**: Printable profiles and donor lists

## Technology Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy
- **Database**: SQLite (auto-created)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.0
- **Authentication**: Flask-Login with bcrypt password hashing
- **Environment**: python-dotenv for configuration

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- PowerShell 7.0+ (Windows)
- Can run without a Virtual Environment.

### Step 1: Clone or Download
```bash
# If using git
git clone https://github.com/Drushyagowda17/BloodLink.git
cd BloodLink

# Or download and extract the ZIP file
```

### Step 2: Install Dependencies
Install each dependency individually:

```bash
python -m pip install flask
python -m pip install flask_sqlalchemy
python -m pip install flask_bcrypt
python -m pip install flask_login
python -m pip install python-dotenv
```

### Step 3: Environment Configuration( NOt needed to run each time  depends on you)
1. Copy `.env.example` to `.env`:        
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   MEDICAL_CHATBOT_PROVIDER=openai
   MEDICAL_CHATBOT_API_KEY=your-api-key-here
   HOSPITAL_CODES=HOSP001,HOSP002,HOSP003,AIIMS001,SGPGI001,KIMS001
   ```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage Guide

### First Time Setup
1. Start the application
2. The SQLite database (`bloodlink.db`) will be created automatically
3. Visit `http://localhost:5000` to access the application

### For Donors
1. **Register**: Go to `/register` and fill out the donor registration form
2. **Login**: Use your email and password to access your dashboard
3. **Profile Management**: Update your information anytime from the dashboard
4. **View History**: Check your blood donation history and statistics

### For Hospitals
1. **Register**: Go to `/Hospital-Register` with a valid hospital code
2. **Login**: Access the hospital dashboard at `/Hospital-Login`
3. **Search Donors**: Use filters to find donors by blood type and location
4. **Record Usage**: Create records when blood is used from donors

### Admin Features
- Hospital codes are managed through the `.env` file
- Add new valid codes by updating the `HOSPITAL_CODES` variable

## File Structure

```
BloodLink/
├── app.py                 # Main Flask application
├── bloodlink.db          # SQLite database (auto-created)
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── styles.css   # Custom styles with theme support
│   ├── js/
│   │   └── scripts.js   # JavaScript functionality
│   └── i18n/
│       ├── en.json      # English translations
│       ├── kn.json      # Kannada translations
│       └── hi.json      # Hindi translations
└── templates/
    ├── base.html            # Base template with navigation
    ├── index.html           # Landing page
    ├── register.html        # Donor registration
    ├── login.html           # Donor login
    ├── dashboard.html       # Donor dashboard
    ├── edit_profile.html    # Profile editing
    ├── hospital_register.html # Hospital registration
    ├── hospital_login.html   # Hospital login
    ├── hospital_dashboard.html # Hospital dashboard
    ├── usage_form.html      # Blood usage recording
    └── error.html           # Error pages
```

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `MEDICAL_CHATBOT_PROVIDER`: Chatbot service provider (openai/infermedica/custom)
- `MEDICAL_CHATBOT_API_KEY`: API key for chatbot service
- `HOSPITAL_CODES`: Comma-separated list of valid hospital codes

### Database
- SQLite database is created automatically on first run
- No migrations required - tables are created using SQLAlchemy
- Database file: `bloodlink.db`

### Customization
- **Themes**: Modify CSS variables in `styles.css`
- **Languages**: Add new translation files in `static/i18n/`
- **Hospital Codes**: Update `.env` file with new codes
- **Chatbot**: Implement custom providers in the `ChatbotAdapter` class

## Security Features

- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure session handling with Flask-Login
- **Data Privacy**: Role-based access control
- **Input Validation**: Server-side and client-side validation
- **CSRF Protection**: Built-in Flask security features

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+
- **Features**: ES6+, CSS Grid, Flexbox, Local Storage

## Troubleshooting

### Common Issues

1. **Database not created**:
   - Ensure Python has write permissions in the directory
   - Check if `bloodlink.db` file is created after first run

2. **Import errors**:
   - Verify all dependencies are installed correctly
   - Use `python -m pip list` to check installed packages

3. **Port already in use**:
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

4. **Chatbot not working**:
   - Check `.env` file configuration
   - Verify API keys are valid
   - Ensure internet connection for external APIs

### Development Mode
- Set `debug=True` in `app.py` for development
- Error details will be shown on error pages
- Auto-reload on file changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- **Email**: drushyagmgowda@gmail.com
- **Issues**: Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Complete donor and hospital management
- Multi-language support
- Responsive design
- Medical assistant chatbot
- Dark/light theme support

---
**Note**:This was built as a collage mini project.
**Note**: This application is designed for educational and demonstration purposes. For production use, additional security measures, proper API integrations, and comprehensive testing should be implemented.# BloodLink

*Any questions contact at : drushyagmgowda@gmail.com


