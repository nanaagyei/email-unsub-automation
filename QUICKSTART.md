# Quick Start Guide

## Email Unsubscribe Automation v2.0

### Prerequisites
- Python 3.6+
- Gmail account with 2FA enabled
- App-specific password for Gmail

### Installation (5 minutes)

1. **Clone and enter directory:**
   ```bash
   git clone https://github.com/nanaagyei/email-unsub-automation.git
   cd email-unsub-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Configure in browser:**
   - Application opens at `http://localhost:8501`
   - Go to "Settings" page
   - Enter your email and app-specific password
   - Click "Save & Test Connection"

### First Use

1. **Settings Page:**
   - Configure your Gmail credentials
   - Test connection

2. **Email Scanner:**
   - Choose number of emails to scan (start with 50)
   - Click "Start Scan"
   - Wait for results

3. **Unsubscribe Manager:**
   - Review found unsubscribe links
   - Select emails to unsubscribe from
   - Click "Unsubscribe Selected"

4. **Dashboard:**
   - View statistics
   - Monitor success rate
   - Check operation history

### Creating App-Specific Password

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to "2-Step Verification" → "App passwords"
4. Generate new password for "Mail"
5. Copy the 16-character password
6. Use in application Settings

### Common Commands

```bash
# Run application
streamlit run app.py

# Run tests
python src/tests/run_tests.py

# Check installation
python -c "from src.utils.config import Config; print('✓ Installation successful')"
```

### Troubleshooting

**Connection fails:**
- Verify app-specific password (not regular password)
- Ensure 2FA is enabled
- Check IMAP is enabled in Gmail settings

**Import errors:**
- Run: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.6+)

**Database errors:**
- Application will create database automatically
- Ensure write permissions in directory

### Features

✅ **Web Interface** - Clean, modern UI
✅ **Email Scanning** - Find all unsubscribe links
✅ **Smart Categories** - Auto-categorize emails
✅ **Whitelist/Blacklist** - Protect important senders
✅ **Statistics** - Track your progress
✅ **Export** - Save your data
✅ **History** - Complete audit log

### Next Steps

1. Add trusted senders to whitelist
2. Run regular scans (weekly recommended)
3. Review statistics to see inbox cleanup progress
4. Export data for records

### Support

- Documentation: README.md
- Detailed Changes: CHANGELOG.md
- Issues: GitHub Issues
- Tests: `python src/tests/run_tests.py`

---

**Happy inbox cleaning! 📧✨**
