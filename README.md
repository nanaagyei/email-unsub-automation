# Email Unsubscribe Automation 2.0

A comprehensive Python application that automates the process of unsubscribing from unwanted emails with a modern web interface, intelligent categorization, and robust tracking.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![Tests](https://img.shields.io/badge/tests-82%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🎨 Modern Web Interface
- **Streamlit-powered** intuitive web UI
- Real-time progress tracking
- Interactive data visualization
- Multi-page application with easy navigation
- Responsive design

### 📧 Smart Email Management
- Automatic email scanning for unsubscribe links
- Intelligent email categorization (Newsletter, Promotion, Marketing, etc.)
- Whitelist/Blacklist management
- Custom filter creation with regex support
- Batch operations

### 🗄️ Persistent Data Storage
- SQLite database for all operations
- Complete operation history
- Statistical analytics
- Export functionality

### 📊 Analytics & Reporting
- Real-time statistics dashboard
- Category breakdown visualization
- Success rate tracking
- Operation history logs
- Export capabilities

### 🔒 Security Features
- Secure credential handling
- App-specific password support
- Link validation (prevents XSS)
- No credential storage to disk
- Rate limiting to respect servers

### 🧪 Comprehensive Testing
- 82+ test cases
- 80%+ code coverage
- Unit and integration tests
- Mock testing for external dependencies

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- Gmail account with App-Specific Password
- pip package manager

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/nanaagyei/email-unsub-automation.git
cd email-unsub-automation
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up credentials (optional - can be done in UI):**
```bash
# Create .env file
touch .env

# Add your credentials
echo "EMAIL=your-email@gmail.com" >> .env
echo "PASSWORD=your-app-specific-password" >> .env
```

5. **Run the application:**
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔐 Security Setup

### Creating an App-Specific Password

**Required:** Gmail requires 2-Factor Authentication and App-Specific Passwords for IMAP access.

1. **Enable 2-Factor Authentication:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Navigate to "2-Step Verification"
   - Follow the setup wizard

2. **Generate App-Specific Password:**
   - In Google Account Security
   - Go to "2-Step Verification"
   - Scroll to "App passwords"
   - Select "Mail" and your device
   - Copy the generated 16-character password
   - Use this password in the application

### Security Best Practices
- ✅ Never commit your `.env` file
- ✅ Never share your app-specific password
- ✅ Rotate passwords regularly
- ✅ Keep 2FA enabled always
- ✅ Monitor account activity
- ✅ Review whitelisted emails periodically

## 🚀 Usage

### Web Interface

After running `streamlit run app.py`, you'll see:

#### 1. Dashboard
- Overview of all statistics
- Quick metrics at a glance
- Category breakdown visualization
- Recent operation logs

#### 2. Email Scanner
- Configure number of emails to scan
- Start scanning with one click
- Real-time progress tracking
- View results immediately

#### 3. Unsubscribe Manager
- View all pending unsubscribe links
- Select individual or bulk unsubscribe
- Filter by email category
- Confirm before unsubscribing

#### 4. Whitelist/Blacklist
- Add email patterns to protect
- Add spam patterns to prioritize
- Supports wildcards (`*@example.com`)
- Supports regex patterns

#### 5. Settings
- Configure email credentials
- Test connection
- Adjust scan parameters
- View security instructions

#### 6. Statistics
- Detailed analytics
- Visual charts and graphs
- Export data functionality
- Success rate analysis

#### 7. Operation History
- Complete audit log
- Filter by type and status
- Search operations
- Troubleshoot issues

### Command Line (Legacy)

The original script functionality is preserved:

```python
from src.core.orchestrator import EmailUnsubscribeOrchestrator
from src.utils.config import Config
from src.utils.logger import setup_logging

# Setup
setup_logging("INFO")
config = Config()
orchestrator = EmailUnsubscribeOrchestrator(config)

# Scan emails
results = orchestrator.scan_emails(max_emails=100)
print(f"Found {results['total_links_found']} unsubscribe links")

# Unsubscribe
orchestrator.unsubscribe_from_links(auto_mode=True)
```

## 📁 Project Structure

```
email-unsub-automation/
├── src/
│   ├── core/              # Core business logic
│   │   ├── email_manager.py
│   │   ├── unsubscribe_handler.py
│   │   └── orchestrator.py
│   ├── database/          # Database models
│   │   └── models.py
│   ├── ui/                # User interface
│   │   └── streamlit_app.py
│   ├── utils/             # Utilities
│   │   ├── config.py
│   │   └── logger.py
│   └── tests/             # Test suite
│       ├── test_database.py
│       ├── test_email_manager.py
│       ├── test_unsubscribe_handler.py
│       ├── test_config.py
│       └── run_tests.py
├── app.py                 # Application entry point
├── main.py                # Legacy script (deprecated)
├── requirements.txt       # Dependencies
├── .env                   # Configuration (create this)
├── .gitignore
├── CHANGELOG.md          # Detailed changes
├── README.md             # This file
└── LICENSE
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python src/tests/run_tests.py

# Or with pytest (if installed)
pytest src/tests/

# Run specific test file
python -m unittest src.tests.test_database
```

### Test Coverage

- **Database Operations:** 28 tests
- **Email Manager:** 23 tests  
- **Unsubscribe Handler:** 16 tests
- **Configuration:** 15 tests
- **Total:** 82+ test cases

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Email credentials (required)
EMAIL=your-email@gmail.com
PASSWORD=your-app-specific-password

# Optional settings
IMAP_SERVER=imap.gmail.com         # Default: imap.gmail.com
DATABASE_PATH=email_automation.db   # Default: email_automation.db
MAX_EMAILS_PER_SCAN=100            # Default: 100
LINK_CLICK_DELAY=1.0               # Default: 1.0 seconds
REQUEST_TIMEOUT=10                  # Default: 10 seconds
```

### In-App Configuration

All settings can be configured through the Settings page in the web interface.

## 📊 Database Schema

The application uses SQLite with the following tables:

- **emails** - Scanned email metadata
- **unsubscribe_links** - Extracted unsubscribe URLs
- **whitelist** - Protected email patterns
- **blacklist** - Unwanted email patterns
- **custom_filters** - User-defined filters
- **operation_history** - Complete audit log
- **settings** - Application configuration

## 🔄 Upgrading from v1.0

If you're using the old `main.py` script:

1. Install new dependencies: `pip install -r requirements.txt`
2. Your `.env` file works without changes
3. Run the new interface: `streamlit run app.py`
4. Old `links.txt` files can be referenced but won't auto-import

See [CHANGELOG.md](CHANGELOG.md) for detailed migration information.

## 🐛 Troubleshooting

### Connection Issues
- ✅ Verify app-specific password is correct
- ✅ Ensure 2FA is enabled
- ✅ Check IMAP is enabled in Gmail settings
- ✅ Test connection in Settings page

### Permission Errors
- ✅ Confirm Gmail IMAP is enabled
- ✅ Verify Google Account security settings
- ✅ Check for unusual activity blocks

### Database Issues
- ✅ Ensure write permissions in app directory
- ✅ Check disk space
- ✅ Delete `email_automation.db` to reset

### UI Issues
- ✅ Clear browser cache
- ✅ Try incognito/private mode
- ✅ Update Streamlit: `pip install --upgrade streamlit`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided as-is without warranties. Features:
- Automates clicking unsubscribe links
- Requires your Gmail credentials (app-specific password)
- May not work with all types of unsubscribe mechanisms
- Some services may require additional verification
- Use at your own discretion
- Always review links before unsubscribing

## 🎯 Roadmap

### Completed ✅
- [x] Web interface with Streamlit
- [x] Database-backed storage
- [x] Email categorization
- [x] Whitelist/Blacklist
- [x] Statistics dashboard
- [x] Operation history
- [x] Comprehensive testing
- [x] Export functionality

### Future Enhancements 🚀
- [ ] Scheduled automatic scans
- [ ] Machine learning for better categorization
- [ ] Multi-account support
- [ ] Email provider plugins (beyond Gmail)
- [ ] Advanced reporting with charts
- [ ] Undo unsubscribe operations
- [ ] Email preview before unsubscribe
- [ ] Browser extension integration

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/nanaagyei/email-unsub-automation/issues)
- **Documentation:** See [CHANGELOG.md](CHANGELOG.md) for detailed changes
- **Security:** Report security issues via GitHub Security tab

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Requests](https://requests.readthedocs.io/) - HTTP client
- [Python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management

---

**Made with ❤️ to help clean up your inbox**
