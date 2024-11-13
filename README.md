# Email Unsubscribe Automation

This Python script automates the process of unsubscribing from unwanted emails by scanning your Gmail inbox for unsubscribe links and automatically clicking them.

## Features

- Connects securely to Gmail using IMAP
- Searches for emails containing "unsubscribe" text
- Extracts unsubscribe links from HTML emails
- Automatically clicks unsubscribe links
- Saves all found links to a file for reference

## Prerequisites

- Python 3.6 or higher
- Gmail account
- App-specific password for Gmail (required for security)

## Installation

1. Clone this repository:
``bash
git clone https://github.com/nanaagyei/email-unsub-automation.git
cd email-unsubscribe-automation
``
2. Install required dependencies:
``bash
pip install -r requirements.txt
``
3. Create a `.env` file in the project root directory:
``bash
touch .env
``
4. Add your Gmail account credentials and app-specific password to the `.env` file:
``bash
EMAIL_ADDRESS=<your-email-address>
EMAIL_PASSWORD=<your-email-password>
``
## Security Setup (Important!)

### Setting up App-Specific Password (Required)
Due to Google's security policies, you'll need to use an App-Specific Password instead of your regular Gmail password:

1. Enable 2-Factor Authentication (2FA) on your Google Account
   - Go to your Google Account settings
   - Navigate to Security
   - Enable "2-Step Verification"

2. Generate an App-Specific Password
   - Go to your Google Account settings
   - Navigate to Security
   - Under "2-Step Verification," scroll to "App passwords"
   - Generate a new app password for "Mail"
   - Use this password in your `.env` file

### Security Precautions

⚠️ **IMPORTANT SECURITY NOTES:**
- Never commit your `.env` file to version control
- Never share your app-specific password with anyone
- Regularly rotate your app-specific password
- Keep your 2FA enabled at all times
- Monitor your account activity regularly

## Usage

Run the script using Python:
``bash
python main.py
``
The script will:
1. Connect to your Gmail account
2. Search for emails containing "unsubscribe"
3. Extract unsubscribe links
4. Attempt to click each link
5. Save all found links to `links.txt`

## File Structure

- `main.py` - Main script containing the automation logic
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not included in repository)
- `links.txt` - Output file containing found unsubscribe links

## Functions

- `connect_to_email()`: Establishes IMAP connection to Gmail
- `extract_links_from_html()`: Parses HTML content for unsubscribe links
- `click_link()`: Attempts to visit unsubscribe links
- `search_for_email()`: Searches inbox for relevant emails
- `save_links()`: Saves found links to file

## Troubleshooting

1. **Connection Issues**
   - Verify your app-specific password is correct
   - Ensure 2FA is properly set up
   - Check your internet connection

2. **Permission Errors**
   - Confirm IMAP is enabled in your Gmail settings
   - Verify your Google Account security settings

## Contributing

Feel free to submit issues and enhancement requests!

## TODO - GUI Enhancement Plans

### Planned GUI Features
1. Email Management Interface
   - Visual inbox viewer
   - Checkbox selection for emails to unsubscribe from
   - Preview of email content before unsubscribing
   - Batch selection/deselection options

2. Progress Tracking
   - Real-time progress bar for unsubscribe operations
   - Success/failure status indicators
   - Detailed logs viewer
   - Statistics dashboard (total processed, success rate, etc.)

3. Settings Configuration
   - GUI for .env file configuration
   - IMAP settings customization
   - Proxy configuration options
   - Theme customization (light/dark mode)

4. Smart Features
   - Sender categorization (newsletters, promotions, etc.)
   - Bulk action recommendations
   - Scheduled unsubscribe operations
   - Email pattern recognition for similar senders

5. Security Enhancements
   - Secure credential storage
   - 2FA setup wizard
   - App-specific password generation guide
   - Security status dashboard

6. Reporting
   - Export unsubscribe history
   - Generate activity reports
   - Email cleanup statistics
   - Visual analytics of email patterns

7. Advanced Features
   - Custom filter creation
   - Whitelist/blacklist management
   - Regular expression support for email searching
   - API integration options

### Technical Implementation Plans
- [ ] Set up PyQt5/tkinter framework
- [ ] Design responsive UI layouts
- [ ] Implement threading for background operations
- [ ] Create database for storing operation history
- [ ] Develop API wrapper for email operations
- [ ] Add unit tests for GUI components
- [ ] Implement error handling and recovery

## License

[Add your chosen license here]

## Disclaimer

This tool is provided as-is without any warranties. Always review unsubscribe links before running automated tools on your email account.