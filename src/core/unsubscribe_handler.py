"""Unsubscribe link handler"""
import requests
import logging
from typing import Dict, Optional
import time


class UnsubscribeHandler:
    """Handles clicking unsubscribe links and tracking results"""
    
    def __init__(self, timeout: int = 10, retry_count: int = 2):
        """Initialize unsubscribe handler"""
        self.timeout = timeout
        self.retry_count = retry_count
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def click_link(self, link: str) -> Dict:
        """
        Attempt to click an unsubscribe link
        
        Returns:
            Dict with status information including:
            - success: bool
            - status_code: int or None
            - error_message: str or None
        """
        result = {
            "success": False,
            "status_code": None,
            "error_message": None,
            "response_time": None
        }
        
        for attempt in range(self.retry_count):
            try:
                start_time = time.time()
                response = self.session.get(link, timeout=self.timeout, allow_redirects=True)
                result["response_time"] = time.time() - start_time
                result["status_code"] = response.status_code
                
                if 200 <= response.status_code < 400:
                    result["success"] = True
                    self.logger.info(f"Successfully clicked link: {link} (Status: {response.status_code})")
                    return result
                else:
                    result["error_message"] = f"HTTP {response.status_code}"
                    self.logger.warning(f"Link returned status {response.status_code}: {link}")
                    
            except requests.exceptions.Timeout:
                result["error_message"] = "Request timeout"
                self.logger.error(f"Timeout clicking link: {link}")
                
            except requests.exceptions.ConnectionError:
                result["error_message"] = "Connection error"
                self.logger.error(f"Connection error for link: {link}")
                
            except requests.exceptions.RequestException as e:
                result["error_message"] = str(e)
                self.logger.error(f"Error clicking link {link}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_count - 1:
                time.sleep(1)
        
        return result
    
    def validate_link(self, link: str) -> bool:
        """Validate if a link is properly formatted and safe"""
        try:
            # Basic URL validation
            if not link.startswith(("http://", "https://")):
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = ["javascript:", "data:", "file:", "ftp:"]
            if any(pattern in link.lower() for pattern in suspicious_patterns):
                return False
            
            return True
        except:
            return False
    
    def batch_click_links(self, links: list, delay: float = 1.0) -> Dict:
        """
        Click multiple links with delay between requests
        
        Returns:
            Dict with summary statistics
        """
        results = {
            "total": len(links),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for link in links:
            if not self.validate_link(link):
                self.logger.warning(f"Skipping invalid link: {link}")
                results["failed"] += 1
                results["details"].append({
                    "link": link,
                    "success": False,
                    "error_message": "Invalid link format"
                })
                continue
            
            result = self.click_link(link)
            result["link"] = link
            results["details"].append(result)
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            # Delay between requests to be respectful
            if delay > 0:
                time.sleep(delay)
        
        return results
