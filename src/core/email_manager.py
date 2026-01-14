"""Email manager for handling IMAP operations and email processing"""
import os
import imaplib
import email as email_module
from email.header import decode_header
from email.message import Message
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import re
import logging


class EmailManager:
    """Manages email connections and operations"""
    
    def __init__(self, email_address: str, password: str, imap_server: str = "imap.gmail.com"):
        """Initialize email manager"""
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.mail = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connect to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            self.mail.select("inbox")
            self.logger.info(f"Successfully connected to {self.imap_server}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to email: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        if self.mail:
            try:
                self.mail.logout()
                self.logger.info("Disconnected from email server")
            except Exception as e:
                self.logger.error(f"Error disconnecting: {str(e)}")
    
    def search_emails(self, criteria: str = '(BODY "unsubscribe")', max_emails: int = None) -> List[bytes]:
        """Search for emails based on criteria"""
        try:
            if not self.mail:
                self.connect()
            
            _, search_data = self.mail.search(None, criteria)
            email_ids = search_data[0].split()
            
            if max_emails:
                email_ids = email_ids[-max_emails:]
            
            self.logger.info(f"Found {len(email_ids)} emails matching criteria")
            return email_ids
        except Exception as e:
            self.logger.error(f"Error searching emails: {str(e)}")
            return []
    
    def fetch_email(self, email_id: bytes) -> Optional[Message]:
        """Fetch a single email by ID"""
        try:
            _, data = self.mail.fetch(email_id, "(RFC822)")
            msg = email_module.message_from_bytes(data[0][1])
            return msg
        except Exception as e:
            self.logger.error(f"Error fetching email {email_id}: {str(e)}")
            return None
    
    def extract_email_data(self, msg: Message) -> Dict:
        """Extract relevant data from email message"""
        try:
            # Get sender
            from_header = msg.get("From", "")
            sender = email_module.utils.parseaddr(from_header)[1]
            
            # Get subject
            subject_header = msg.get("Subject", "")
            subject = self._decode_header(subject_header)
            
            # Get date
            date_header = msg.get("Date", "")
            try:
                received_date = email_module.utils.parsedate_to_datetime(date_header)
            except:
                received_date = datetime.now()
            
            # Get message ID
            message_id = msg.get("Message-ID", "")
            
            return {
                "message_id": message_id,
                "sender": sender,
                "subject": subject,
                "received_date": received_date,
                "from_header": from_header
            }
        except Exception as e:
            self.logger.error(f"Error extracting email data: {str(e)}")
            return {}
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or "utf-8", errors="ignore")
                else:
                    decoded_string += part
            return decoded_string
        except:
            return header
    
    def extract_html_content(self, msg: Message) -> List[str]:
        """Extract HTML content from email"""
        html_parts = []
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        try:
                            html_content = part.get_payload(decode=True).decode(errors="ignore")
                            html_parts.append(html_content)
                        except:
                            pass
            else:
                if msg.get_content_type() == "text/html":
                    try:
                        html_content = msg.get_payload(decode=True).decode(errors="ignore")
                        html_parts.append(html_content)
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"Error extracting HTML content: {str(e)}")
        
        return html_parts
    
    def extract_unsubscribe_links(self, html_content: str) -> List[str]:
        """Extract unsubscribe links from HTML content"""
        links = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Find all links with "unsubscribe" in href or text
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text().lower()
                
                if "unsubscribe" in href.lower() or "unsubscribe" in text:
                    # Clean up the link
                    if href.startswith("http"):
                        links.append(href)
            
            # Also check for List-Unsubscribe header links
            # This would be done in the main processing function
            
        except Exception as e:
            self.logger.error(f"Error extracting unsubscribe links: {str(e)}")
        
        return list(set(links))  # Remove duplicates
    
    def categorize_email(self, sender: str, subject: str) -> str:
        """Categorize email based on sender and subject"""
        sender_lower = sender.lower()
        subject_lower = subject.lower()
        
        # Social media indicators (check first as they're more specific)
        social_keywords = ["facebook", "twitter", "linkedin", "instagram", "social"]
        if any(keyword in sender_lower for keyword in social_keywords):
            return "social"
        
        # Newsletter indicators
        newsletter_keywords = ["newsletter", "digest", "weekly", "monthly", "bulletin"]
        if any(keyword in sender_lower or keyword in subject_lower for keyword in newsletter_keywords):
            return "newsletter"
        
        # Promotion indicators
        promotion_keywords = ["offer", "deal", "sale", "discount", "promo", "save", "shop"]
        if any(keyword in subject_lower for keyword in promotion_keywords):
            return "promotion"
        
        # Marketing indicators
        marketing_keywords = ["marketing", "advertisement", "campaign"]
        if any(keyword in sender_lower or keyword in subject_lower for keyword in marketing_keywords):
            return "marketing"
        
        # Notification indicators
        notification_keywords = ["notification", "alert", "reminder", "update"]
        if any(keyword in subject_lower for keyword in notification_keywords):
            return "notification"
        
        return "uncategorized"
    
    def check_whitelist_blacklist(self, sender: str, whitelist: List[str], blacklist: List[str]) -> Tuple[bool, str]:
        """Check if sender matches whitelist or blacklist patterns"""
        sender_lower = sender.lower()
        
        # Check whitelist first
        for pattern in whitelist:
            if self._match_pattern(sender_lower, pattern.lower()):
                return True, "whitelisted"
        
        # Check blacklist
        for pattern in blacklist:
            if self._match_pattern(sender_lower, pattern.lower()):
                return True, "blacklisted"
        
        return False, "none"
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """Match text against a pattern (supports wildcards and regex)"""
        try:
            # Simple wildcard matching
            if "*" in pattern:
                pattern_regex = pattern.replace("*", ".*")
                return bool(re.match(pattern_regex, text))
            
            # Exact match
            if pattern in text:
                return True
            
            # Try as regex
            try:
                return bool(re.search(pattern, text))
            except:
                return False
        except:
            return False
    
    def get_list_unsubscribe_header(self, msg: Message) -> Optional[str]:
        """Get List-Unsubscribe header if present"""
        try:
            return msg.get("List-Unsubscribe", None)
        except:
            return None
