"""Main orchestrator for email unsubscribe automation"""
from typing import List, Dict, Optional, Callable
import logging
from datetime import datetime

from src.core.email_manager import EmailManager
from src.core.unsubscribe_handler import UnsubscribeHandler
from src.database.models import Database
from src.utils.config import Config
from src.utils.logger import setup_logging


class EmailUnsubscribeOrchestrator:
    """Main orchestrator for email unsubscribe operations"""
    
    def __init__(self, config: Config, db: Database = None):
        """Initialize orchestrator"""
        self.config = config
        self.db = db or Database(config.database_path)
        self.email_manager = EmailManager(
            config.email_address,
            config.email_password,
            config.imap_server
        )
        self.unsubscribe_handler = UnsubscribeHandler(
            timeout=config.request_timeout,
            retry_count=2
        )
        self.logger = logging.getLogger(__name__)
    
    def scan_emails(self, max_emails: int = None, progress_callback: Callable = None) -> Dict:
        """
        Scan emails for unsubscribe links
        
        Args:
            max_emails: Maximum number of emails to scan
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with scan results
        """
        results = {
            "total_scanned": 0,
            "emails_with_links": 0,
            "total_links_found": 0,
            "errors": 0,
            "emails_processed": []
        }
        
        try:
            # Connect to email
            if not self.email_manager.connect():
                self.logger.error("Failed to connect to email server")
                return results
            
            # Get whitelist and blacklist
            whitelist = [item["email_pattern"] for item in self.db.get_whitelist()]
            blacklist = [item["email_pattern"] for item in self.db.get_blacklist()]
            
            # Search for emails
            max_emails = max_emails or self.config.max_emails_per_scan
            email_ids = self.email_manager.search_emails(max_emails=max_emails)
            results["total_scanned"] = len(email_ids)
            
            self.logger.info(f"Processing {len(email_ids)} emails")
            
            # Process each email
            for idx, email_id in enumerate(email_ids):
                try:
                    # Progress callback
                    if progress_callback:
                        progress_callback(idx + 1, len(email_ids))
                    
                    # Fetch email
                    msg = self.email_manager.fetch_email(email_id)
                    if not msg:
                        continue
                    
                    # Extract email data
                    email_data = self.email_manager.extract_email_data(msg)
                    if not email_data:
                        continue
                    
                    # Check whitelist/blacklist
                    is_listed, list_type = self.email_manager.check_whitelist_blacklist(
                        email_data["sender"], whitelist, blacklist
                    )
                    
                    if list_type == "whitelisted":
                        self.logger.info(f"Skipping whitelisted sender: {email_data['sender']}")
                        continue
                    
                    # Categorize email
                    category = self.email_manager.categorize_email(
                        email_data["sender"],
                        email_data["subject"]
                    )
                    
                    # Save email to database
                    email_db_id = self.db.add_email(
                        email_data["message_id"],
                        email_data["sender"],
                        email_data["subject"],
                        email_data["received_date"],
                        category
                    )
                    
                    # Extract HTML content
                    html_parts = self.email_manager.extract_html_content(msg)
                    
                    # Extract unsubscribe links
                    all_links = []
                    for html in html_parts:
                        links = self.email_manager.extract_unsubscribe_links(html)
                        all_links.extend(links)
                    
                    # Also check List-Unsubscribe header
                    list_unsub = self.email_manager.get_list_unsubscribe_header(msg)
                    if list_unsub:
                        # Parse List-Unsubscribe header
                        import re
                        urls = re.findall(r'<(https?://[^>]+)>', list_unsub)
                        all_links.extend(urls)
                    
                    # Remove duplicates
                    all_links = list(set(all_links))
                    
                    # Save links to database
                    if all_links:
                        results["emails_with_links"] += 1
                        results["total_links_found"] += len(all_links)
                        
                        for link in all_links:
                            self.db.add_unsubscribe_link(email_db_id, link)
                        
                        self.db.mark_email_processed(email_db_id, has_unsubscribe=True)
                    else:
                        self.db.mark_email_processed(email_db_id, has_unsubscribe=False)
                    
                    # Log operation
                    self.db.log_operation(
                        "scan",
                        email_db_id,
                        "success",
                        f"Found {len(all_links)} unsubscribe links"
                    )
                    
                    results["emails_processed"].append({
                        "sender": email_data["sender"],
                        "subject": email_data["subject"],
                        "links_found": len(all_links),
                        "category": category
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing email {email_id}: {str(e)}")
                    results["errors"] += 1
                    self.db.log_operation("scan", None, "error", str(e))
            
            # Disconnect
            self.email_manager.disconnect()
            
        except Exception as e:
            self.logger.error(f"Error during email scan: {str(e)}")
            results["errors"] += 1
        
        return results
    
    def unsubscribe_from_links(self, link_ids: List[int] = None, 
                              auto_mode: bool = False,
                              progress_callback: Callable = None) -> Dict:
        """
        Unsubscribe from selected links
        
        Args:
            link_ids: List of link IDs to unsubscribe from. If None, processes all unclicked links.
            auto_mode: If True, automatically clicks all unclicked links
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dictionary with unsubscribe results
        """
        results = {
            "total_attempted": 0,
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        try:
            # Get links to process
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if link_ids:
                placeholders = ",".join("?" * len(link_ids))
                cursor.execute(f"""
                    SELECT id, link FROM unsubscribe_links 
                    WHERE id IN ({placeholders}) AND clicked = 0
                """, link_ids)
            elif auto_mode:
                cursor.execute("""
                    SELECT id, link FROM unsubscribe_links 
                    WHERE clicked = 0
                """)
            else:
                return results
            
            links_to_process = cursor.fetchall()
            results["total_attempted"] = len(links_to_process)
            
            self.logger.info(f"Processing {len(links_to_process)} unsubscribe links")
            
            # Process each link
            for idx, (link_id, link) in enumerate(links_to_process):
                try:
                    # Progress callback
                    if progress_callback:
                        progress_callback(idx + 1, len(links_to_process))
                    
                    # Click the link
                    result = self.unsubscribe_handler.click_link(link)
                    
                    # Update database
                    self.db.update_link_status(
                        link_id,
                        clicked=True,
                        status_code=result["status_code"],
                        error_message=result["error_message"]
                    )
                    
                    if result["success"]:
                        results["successful"] += 1
                        self.db.log_operation(
                            "unsubscribe",
                            None,
                            "success",
                            f"Successfully unsubscribed: {link}"
                        )
                    else:
                        results["failed"] += 1
                        self.db.log_operation(
                            "unsubscribe",
                            None,
                            "failed",
                            f"Failed to unsubscribe: {link} - {result.get('error_message')}"
                        )
                    
                    results["details"].append({
                        "link_id": link_id,
                        "link": link,
                        "success": result["success"],
                        "status_code": result["status_code"],
                        "error_message": result["error_message"]
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing link {link_id}: {str(e)}")
                    results["failed"] += 1
                    self.db.log_operation("unsubscribe", None, "error", str(e))
            
        except Exception as e:
            self.logger.error(f"Error during unsubscribe operation: {str(e)}")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about operations"""
        return self.db.get_statistics()
    
    def get_recent_operations(self, limit: int = 50) -> List[Dict]:
        """Get recent operations"""
        return self.db.get_recent_operations(limit)
    
    def export_links(self, filename: str = "unsubscribe_links.txt"):
        """Export all unsubscribe links to a file"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ul.link, e.sender, e.subject, ul.clicked, ul.click_timestamp
                FROM unsubscribe_links ul
                JOIN emails e ON ul.email_id = e.id
                ORDER BY ul.created_at DESC
            """)
            
            with open(filename, "w") as f:
                f.write("Email Unsubscribe Links Export\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                for row in cursor.fetchall():
                    link, sender, subject, clicked, click_time = row
                    f.write(f"Sender: {sender}\n")
                    f.write(f"Subject: {subject}\n")
                    f.write(f"Link: {link}\n")
                    f.write(f"Clicked: {'Yes' if clicked else 'No'}\n")
                    if click_time:
                        f.write(f"Click Time: {click_time}\n")
                    f.write("-" * 80 + "\n")
            
            self.logger.info(f"Exported links to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting links: {str(e)}")
            return False
