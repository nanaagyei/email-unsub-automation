"""Configuration management"""
import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application"""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration"""
        load_dotenv(env_file)
        self.env_file = env_file
    
    @property
    def email_address(self) -> Optional[str]:
        """Get email address from environment"""
        return os.getenv("EMAIL") or os.getenv("EMAIL_ADDRESS")
    
    @property
    def email_password(self) -> Optional[str]:
        """Get email password from environment"""
        return os.getenv("PASSWORD") or os.getenv("EMAIL_PASSWORD")
    
    @property
    def imap_server(self) -> str:
        """Get IMAP server, default to Gmail"""
        return os.getenv("IMAP_SERVER", "imap.gmail.com")
    
    @property
    def database_path(self) -> str:
        """Get database path"""
        return os.getenv("DATABASE_PATH", "email_automation.db")
    
    @property
    def max_emails_per_scan(self) -> int:
        """Get maximum emails to scan per operation"""
        try:
            return int(os.getenv("MAX_EMAILS_PER_SCAN", "100"))
        except:
            return 100
    
    @property
    def link_click_delay(self) -> float:
        """Get delay between link clicks"""
        try:
            return float(os.getenv("LINK_CLICK_DELAY", "1.0"))
        except:
            return 1.0
    
    @property
    def request_timeout(self) -> int:
        """Get request timeout in seconds"""
        try:
            return int(os.getenv("REQUEST_TIMEOUT", "10"))
        except:
            return 10
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate that required configuration is present
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.email_address:
            return False, "Email address not configured. Please set EMAIL or EMAIL_ADDRESS in .env"
        
        if not self.email_password:
            return False, "Email password not configured. Please set PASSWORD or EMAIL_PASSWORD in .env"
        
        return True, ""
    
    def set_credentials(self, email_address: str, password: str):
        """Set email credentials (for GUI use)"""
        os.environ["EMAIL"] = email_address
        os.environ["PASSWORD"] = password
