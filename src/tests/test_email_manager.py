"""Tests for email manager"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import email as email_module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.email_manager import EmailManager


class TestEmailManager(unittest.TestCase):
    """Test cases for EmailManager class"""
    
    def setUp(self):
        """Set up test email manager"""
        self.manager = EmailManager("test@example.com", "password", "imap.test.com")
    
    def test_initialization(self):
        """Test EmailManager initialization"""
        self.assertEqual(self.manager.email_address, "test@example.com")
        self.assertEqual(self.manager.password, "password")
        self.assertEqual(self.manager.imap_server, "imap.test.com")
        self.assertIsNone(self.manager.mail)
    
    def test_extract_email_data(self):
        """Test extracting data from email message"""
        # Create a test email
        msg = MIMEMultipart()
        msg['From'] = '"Test Sender" <sender@example.com>'
        msg['Subject'] = 'Test Subject'
        msg['Date'] = 'Mon, 01 Jan 2024 12:00:00 +0000'
        msg['Message-ID'] = '<test123@example.com>'
        
        data = self.manager.extract_email_data(msg)
        
        self.assertEqual(data['sender'], 'sender@example.com')
        self.assertEqual(data['subject'], 'Test Subject')
        self.assertEqual(data['message_id'], '<test123@example.com>')
        self.assertIsInstance(data['received_date'], datetime)
    
    def test_extract_unsubscribe_links(self):
        """Test extracting unsubscribe links from HTML"""
        html = """
        <html>
            <body>
                <p>Newsletter content</p>
                <a href="https://example.com/unsubscribe">Unsubscribe</a>
                <a href="https://example.com/other">Other link</a>
                <a href="https://example.com/unsub">Click here to unsubscribe</a>
            </body>
        </html>
        """
        
        links = self.manager.extract_unsubscribe_links(html)
        
        self.assertEqual(len(links), 2)
        self.assertIn("https://example.com/unsubscribe", links)
        self.assertIn("https://example.com/unsub", links)
    
    def test_categorize_email_newsletter(self):
        """Test categorizing newsletter emails"""
        category = self.manager.categorize_email(
            "newsletter@example.com",
            "Weekly Newsletter Digest"
        )
        
        self.assertEqual(category, "newsletter")
    
    def test_categorize_email_promotion(self):
        """Test categorizing promotional emails"""
        category = self.manager.categorize_email(
            "sales@example.com",
            "Special Offer - 50% Discount!"
        )
        
        self.assertEqual(category, "promotion")
    
    def test_categorize_email_marketing(self):
        """Test categorizing marketing emails"""
        category = self.manager.categorize_email(
            "marketing@example.com",
            "New Product Launch"
        )
        
        self.assertEqual(category, "marketing")
    
    def test_categorize_email_notification(self):
        """Test categorizing notification emails"""
        category = self.manager.categorize_email(
            "notify@example.com",
            "Important Notification: Account Update"
        )
        
        self.assertEqual(category, "notification")
    
    def test_categorize_email_social(self):
        """Test categorizing social media emails"""
        category = self.manager.categorize_email(
            "noreply@facebook.com",
            "You have new notifications"
        )
        
        self.assertEqual(category, "social")
    
    def test_categorize_email_uncategorized(self):
        """Test uncategorized emails"""
        category = self.manager.categorize_email(
            "random@example.com",
            "Random subject"
        )
        
        self.assertEqual(category, "uncategorized")
    
    def test_match_pattern_exact(self):
        """Test exact pattern matching"""
        result = self.manager._match_pattern("test@example.com", "example.com")
        self.assertTrue(result)
        
        result = self.manager._match_pattern("test@example.com", "other.com")
        self.assertFalse(result)
    
    def test_match_pattern_wildcard(self):
        """Test wildcard pattern matching"""
        result = self.manager._match_pattern("test@example.com", "*@example.com")
        self.assertTrue(result)
        
        result = self.manager._match_pattern("newsletter@test.com", "newsletter@*")
        self.assertTrue(result)
        
        result = self.manager._match_pattern("test@example.com", "*newsletter*")
        self.assertFalse(result)
    
    def test_check_whitelist_blacklist(self):
        """Test whitelist/blacklist checking"""
        whitelist = ["*@trusted.com", "important@*"]
        blacklist = ["*@spam.com", "newsletter@*"]
        
        # Test whitelisted
        is_listed, list_type = self.manager.check_whitelist_blacklist(
            "test@trusted.com", whitelist, blacklist
        )
        self.assertTrue(is_listed)
        self.assertEqual(list_type, "whitelisted")
        
        # Test blacklisted
        is_listed, list_type = self.manager.check_whitelist_blacklist(
            "test@spam.com", whitelist, blacklist
        )
        self.assertTrue(is_listed)
        self.assertEqual(list_type, "blacklisted")
        
        # Test neither
        is_listed, list_type = self.manager.check_whitelist_blacklist(
            "test@example.com", whitelist, blacklist
        )
        self.assertFalse(is_listed)
        self.assertEqual(list_type, "none")
    
    def test_decode_header(self):
        """Test header decoding"""
        # Test simple header
        result = self.manager._decode_header("Simple Subject")
        self.assertEqual(result, "Simple Subject")
        
        # Test UTF-8 encoded header (simulated)
        result = self.manager._decode_header("Test Subject")
        self.assertIsInstance(result, str)
    
    def test_extract_html_content_multipart(self):
        """Test extracting HTML from multipart email"""
        msg = MIMEMultipart('alternative')
        
        # Add plain text part
        text_part = MIMEText("Plain text content", 'plain')
        msg.attach(text_part)
        
        # Add HTML part
        html_part = MIMEText("<html><body>HTML content</body></html>", 'html')
        msg.attach(html_part)
        
        html_parts = self.manager.extract_html_content(msg)
        
        self.assertEqual(len(html_parts), 1)
        self.assertIn("HTML content", html_parts[0])
    
    def test_extract_html_content_single(self):
        """Test extracting HTML from single-part email"""
        msg = MIMEText("<html><body>HTML content</body></html>", 'html')
        
        html_parts = self.manager.extract_html_content(msg)
        
        self.assertEqual(len(html_parts), 1)
        self.assertIn("HTML content", html_parts[0])
    
    def test_get_list_unsubscribe_header(self):
        """Test getting List-Unsubscribe header"""
        msg = MIMEMultipart()
        msg['List-Unsubscribe'] = '<https://example.com/unsubscribe>'
        
        header = self.manager.get_list_unsubscribe_header(msg)
        
        self.assertEqual(header, '<https://example.com/unsubscribe>')
    
    def test_extract_unsubscribe_links_no_links(self):
        """Test extracting unsubscribe links when none present"""
        html = """
        <html>
            <body>
                <p>Newsletter content</p>
                <a href="https://example.com">Regular link</a>
            </body>
        </html>
        """
        
        links = self.manager.extract_unsubscribe_links(html)
        
        self.assertEqual(len(links), 0)
    
    def test_extract_unsubscribe_links_case_insensitive(self):
        """Test case-insensitive unsubscribe link extraction"""
        html = """
        <html>
            <body>
                <a href="https://example.com/UNSUBSCRIBE">UNSUBSCRIBE</a>
                <a href="https://example.com/UnSub">UnSubscribe Here</a>
            </body>
        </html>
        """
        
        links = self.manager.extract_unsubscribe_links(html)
        
        self.assertEqual(len(links), 2)


class TestEmailManagerIntegration(unittest.TestCase):
    """Integration tests for EmailManager (requires mocking IMAP)"""
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_success(self, mock_imap):
        """Test successful connection"""
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        
        manager = EmailManager("test@example.com", "password")
        result = manager.connect()
        
        self.assertTrue(result)
        mock_mail.login.assert_called_once_with("test@example.com", "password")
        mock_mail.select.assert_called_once_with("inbox")
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_failure(self, mock_imap):
        """Test connection failure"""
        mock_imap.side_effect = Exception("Connection failed")
        
        manager = EmailManager("test@example.com", "password")
        result = manager.connect()
        
        self.assertFalse(result)
    
    @patch('imaplib.IMAP4_SSL')
    def test_disconnect(self, mock_imap):
        """Test disconnection"""
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail
        
        manager = EmailManager("test@example.com", "password")
        manager.connect()
        manager.disconnect()
        
        mock_mail.logout.assert_called_once()


if __name__ == "__main__":
    unittest.main()
