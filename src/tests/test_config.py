"""Tests for configuration"""
import unittest
import os
from unittest.mock import patch

from src.utils.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class"""
    
    def setUp(self):
        """Set up test configuration"""
        # Clear environment variables
        for key in ['EMAIL', 'EMAIL_ADDRESS', 'PASSWORD', 'EMAIL_PASSWORD', 
                    'IMAP_SERVER', 'DATABASE_PATH', 'MAX_EMAILS_PER_SCAN',
                    'LINK_CLICK_DELAY', 'REQUEST_TIMEOUT']:
            if key in os.environ:
                del os.environ[key]
    
    def test_email_address_from_EMAIL(self):
        """Test getting email address from EMAIL env var"""
        os.environ['EMAIL'] = 'test@example.com'
        config = Config()
        self.assertEqual(config.email_address, 'test@example.com')
    
    def test_email_address_from_EMAIL_ADDRESS(self):
        """Test getting email address from EMAIL_ADDRESS env var"""
        os.environ['EMAIL_ADDRESS'] = 'test@example.com'
        config = Config()
        self.assertEqual(config.email_address, 'test@example.com')
    
    def test_email_address_priority(self):
        """Test EMAIL takes priority over EMAIL_ADDRESS"""
        os.environ['EMAIL'] = 'primary@example.com'
        os.environ['EMAIL_ADDRESS'] = 'secondary@example.com'
        config = Config()
        self.assertEqual(config.email_address, 'primary@example.com')
    
    def test_email_password_from_PASSWORD(self):
        """Test getting password from PASSWORD env var"""
        os.environ['PASSWORD'] = 'secret123'
        config = Config()
        self.assertEqual(config.email_password, 'secret123')
    
    def test_email_password_from_EMAIL_PASSWORD(self):
        """Test getting password from EMAIL_PASSWORD env var"""
        os.environ['EMAIL_PASSWORD'] = 'secret123'
        config = Config()
        self.assertEqual(config.email_password, 'secret123')
    
    def test_imap_server_default(self):
        """Test default IMAP server"""
        config = Config()
        self.assertEqual(config.imap_server, 'imap.gmail.com')
    
    def test_imap_server_custom(self):
        """Test custom IMAP server"""
        os.environ['IMAP_SERVER'] = 'imap.custom.com'
        config = Config()
        self.assertEqual(config.imap_server, 'imap.custom.com')
    
    def test_database_path_default(self):
        """Test default database path"""
        config = Config()
        self.assertEqual(config.database_path, 'email_automation.db')
    
    def test_database_path_custom(self):
        """Test custom database path"""
        os.environ['DATABASE_PATH'] = '/custom/path/db.sqlite'
        config = Config()
        self.assertEqual(config.database_path, '/custom/path/db.sqlite')
    
    def test_max_emails_per_scan_default(self):
        """Test default max emails per scan"""
        config = Config()
        self.assertEqual(config.max_emails_per_scan, 100)
    
    def test_max_emails_per_scan_custom(self):
        """Test custom max emails per scan"""
        os.environ['MAX_EMAILS_PER_SCAN'] = '250'
        config = Config()
        self.assertEqual(config.max_emails_per_scan, 250)
    
    def test_max_emails_per_scan_invalid(self):
        """Test invalid max emails per scan falls back to default"""
        os.environ['MAX_EMAILS_PER_SCAN'] = 'invalid'
        config = Config()
        self.assertEqual(config.max_emails_per_scan, 100)
    
    def test_link_click_delay_default(self):
        """Test default link click delay"""
        config = Config()
        self.assertEqual(config.link_click_delay, 1.0)
    
    def test_link_click_delay_custom(self):
        """Test custom link click delay"""
        os.environ['LINK_CLICK_DELAY'] = '2.5'
        config = Config()
        self.assertEqual(config.link_click_delay, 2.5)
    
    def test_link_click_delay_invalid(self):
        """Test invalid link click delay falls back to default"""
        os.environ['LINK_CLICK_DELAY'] = 'invalid'
        config = Config()
        self.assertEqual(config.link_click_delay, 1.0)
    
    def test_request_timeout_default(self):
        """Test default request timeout"""
        config = Config()
        self.assertEqual(config.request_timeout, 10)
    
    def test_request_timeout_custom(self):
        """Test custom request timeout"""
        os.environ['REQUEST_TIMEOUT'] = '30'
        config = Config()
        self.assertEqual(config.request_timeout, 30)
    
    def test_request_timeout_invalid(self):
        """Test invalid request timeout falls back to default"""
        os.environ['REQUEST_TIMEOUT'] = 'invalid'
        config = Config()
        self.assertEqual(config.request_timeout, 10)
    
    def test_validate_missing_email(self):
        """Test validation fails without email"""
        config = Config()
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn("Email address", error)
    
    def test_validate_missing_password(self):
        """Test validation fails without password"""
        os.environ['EMAIL'] = 'test@example.com'
        config = Config()
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn("password", error)
    
    def test_validate_success(self):
        """Test validation succeeds with all required fields"""
        os.environ['EMAIL'] = 'test@example.com'
        os.environ['PASSWORD'] = 'secret123'
        config = Config()
        is_valid, error = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_set_credentials(self):
        """Test setting credentials programmatically"""
        config = Config()
        config.set_credentials('new@example.com', 'newpassword')
        
        self.assertEqual(os.environ['EMAIL'], 'new@example.com')
        self.assertEqual(os.environ['PASSWORD'], 'newpassword')
        self.assertEqual(config.email_address, 'new@example.com')
        self.assertEqual(config.email_password, 'newpassword')


if __name__ == "__main__":
    unittest.main()
