"""Tests for unsubscribe handler"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests

from src.core.unsubscribe_handler import UnsubscribeHandler


class TestUnsubscribeHandler(unittest.TestCase):
    """Test cases for UnsubscribeHandler class"""
    
    def setUp(self):
        """Set up test unsubscribe handler"""
        self.handler = UnsubscribeHandler(timeout=5, retry_count=1)
    
    def test_initialization(self):
        """Test UnsubscribeHandler initialization"""
        self.assertEqual(self.handler.timeout, 5)
        self.assertEqual(self.handler.retry_count, 1)
        self.assertIsNotNone(self.handler.session)
    
    def test_validate_link_valid_http(self):
        """Test validating valid HTTP link"""
        result = self.handler.validate_link("http://example.com/unsubscribe")
        self.assertTrue(result)
    
    def test_validate_link_valid_https(self):
        """Test validating valid HTTPS link"""
        result = self.handler.validate_link("https://example.com/unsubscribe")
        self.assertTrue(result)
    
    def test_validate_link_invalid_no_protocol(self):
        """Test validating link without protocol"""
        result = self.handler.validate_link("example.com/unsubscribe")
        self.assertFalse(result)
    
    def test_validate_link_invalid_javascript(self):
        """Test validating javascript: link (security)"""
        result = self.handler.validate_link("javascript:alert('xss')")
        self.assertFalse(result)
    
    def test_validate_link_invalid_data(self):
        """Test validating data: link (security)"""
        result = self.handler.validate_link("data:text/html,<script>alert('xss')</script>")
        self.assertFalse(result)
    
    def test_validate_link_invalid_file(self):
        """Test validating file: link (security)"""
        result = self.handler.validate_link("file:///etc/passwd")
        self.assertFalse(result)
    
    @patch('requests.Session.get')
    def test_click_link_success(self, mock_get):
        """Test successful link click"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertIsNone(result['error_message'])
        self.assertIsNotNone(result['response_time'])
    
    @patch('requests.Session.get')
    def test_click_link_redirect(self, mock_get):
        """Test link click with redirect (still successful)"""
        mock_response = Mock()
        mock_response.status_code = 302
        mock_get.return_value = mock_response
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 302)
    
    @patch('requests.Session.get')
    def test_click_link_not_found(self, mock_get):
        """Test link click with 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 404)
        self.assertEqual(result['error_message'], 'HTTP 404')
    
    @patch('requests.Session.get')
    def test_click_link_server_error(self, mock_get):
        """Test link click with 500 error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 500)
    
    @patch('requests.Session.get')
    def test_click_link_timeout(self, mock_get):
        """Test link click with timeout"""
        mock_get.side_effect = requests.exceptions.Timeout
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_message'], 'Request timeout')
        self.assertIsNone(result['status_code'])
    
    @patch('requests.Session.get')
    def test_click_link_connection_error(self, mock_get):
        """Test link click with connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_message'], 'Connection error')
    
    @patch('requests.Session.get')
    def test_click_link_request_exception(self, mock_get):
        """Test link click with general request exception"""
        mock_get.side_effect = requests.exceptions.RequestException("Unknown error")
        
        result = self.handler.click_link("https://example.com/unsubscribe")
        
        self.assertFalse(result['success'])
        self.assertIn("Unknown error", result['error_message'])
    
    @patch('requests.Session.get')
    def test_click_link_retry(self, mock_get):
        """Test link click retry on failure"""
        handler = UnsubscribeHandler(timeout=5, retry_count=3)
        
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        result = handler.click_link("https://example.com/unsubscribe")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('requests.Session.get')
    @patch('time.sleep')
    def test_batch_click_links(self, mock_sleep, mock_get):
        """Test batch clicking multiple links"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        links = [
            "https://example.com/unsubscribe1",
            "https://example.com/unsubscribe2",
            "https://example.com/unsubscribe3"
        ]
        
        result = self.handler.batch_click_links(links, delay=0.5)
        
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['successful'], 3)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(result['details']), 3)
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('requests.Session.get')
    def test_batch_click_links_with_invalid(self, mock_get):
        """Test batch clicking with invalid links"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        links = [
            "https://example.com/unsubscribe",
            "invalid-link",
            "javascript:alert('xss')"
        ]
        
        result = self.handler.batch_click_links(links, delay=0)
        
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['successful'], 1)
        self.assertEqual(result['failed'], 2)
    
    @patch('requests.Session.get')
    def test_batch_click_links_mixed_results(self, mock_get):
        """Test batch clicking with mixed success/failure"""
        # First link succeeds, second fails
        mock_success = Mock()
        mock_success.status_code = 200
        
        mock_fail = Mock()
        mock_fail.status_code = 404
        
        mock_get.side_effect = [mock_success, mock_fail]
        
        links = [
            "https://example.com/unsubscribe1",
            "https://example.com/unsubscribe2"
        ]
        
        result = self.handler.batch_click_links(links, delay=0)
        
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['successful'], 1)
        self.assertEqual(result['failed'], 1)


if __name__ == "__main__":
    unittest.main()
