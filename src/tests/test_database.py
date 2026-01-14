"""Tests for database models"""
import unittest
import os
import tempfile
from datetime import datetime

from src.database.models import Database


class TestDatabase(unittest.TestCase):
    """Test cases for Database class"""
    
    def setUp(self):
        """Set up test database"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_creation(self):
        """Test database file is created"""
        self.assertTrue(os.path.exists(self.temp_db.name))
    
    def test_tables_created(self):
        """Test all tables are created"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'blacklist',
            'custom_filters',
            'emails',
            'operation_history',
            'settings',
            'unsubscribe_links',
            'whitelist'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not created")
    
    def test_add_email(self):
        """Test adding an email"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test Subject",
            received_date=datetime.now(),
            category="newsletter"
        )
        
        self.assertIsNotNone(email_id)
        self.assertIsInstance(email_id, int)
    
    def test_add_duplicate_email(self):
        """Test adding duplicate email returns existing ID"""
        email_id1 = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test Subject",
            received_date=datetime.now()
        )
        
        email_id2 = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test Subject",
            received_date=datetime.now()
        )
        
        self.assertEqual(email_id1, email_id2)
    
    def test_add_unsubscribe_link(self):
        """Test adding an unsubscribe link"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test",
            received_date=datetime.now()
        )
        
        link_id = self.db.add_unsubscribe_link(email_id, "https://example.com/unsubscribe")
        
        self.assertIsNotNone(link_id)
        self.assertIsInstance(link_id, int)
    
    def test_update_link_status(self):
        """Test updating link status"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test",
            received_date=datetime.now()
        )
        
        link_id = self.db.add_unsubscribe_link(email_id, "https://example.com/unsubscribe")
        
        self.db.update_link_status(link_id, True, 200, None)
        
        # Verify update
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT clicked, status_code FROM unsubscribe_links WHERE id = ?", (link_id,))
        result = cursor.fetchone()
        
        self.assertEqual(result[0], 1)  # clicked = True (1 in SQLite)
        self.assertEqual(result[1], 200)
    
    def test_whitelist_operations(self):
        """Test whitelist add, get, and remove"""
        # Add to whitelist
        result = self.db.add_to_whitelist("*@example.com", "Test pattern")
        self.assertTrue(result)
        
        # Get whitelist
        whitelist = self.db.get_whitelist()
        self.assertEqual(len(whitelist), 1)
        self.assertEqual(whitelist[0]["email_pattern"], "*@example.com")
        
        # Try adding duplicate
        result = self.db.add_to_whitelist("*@example.com", "Duplicate")
        self.assertFalse(result)
        
        # Remove from whitelist
        self.db.remove_from_whitelist(whitelist[0]["id"])
        whitelist = self.db.get_whitelist()
        self.assertEqual(len(whitelist), 0)
    
    def test_blacklist_operations(self):
        """Test blacklist add, get, and remove"""
        # Add to blacklist
        result = self.db.add_to_blacklist("*@spam.com", "Spam sender")
        self.assertTrue(result)
        
        # Get blacklist
        blacklist = self.db.get_blacklist()
        self.assertEqual(len(blacklist), 1)
        self.assertEqual(blacklist[0]["email_pattern"], "*@spam.com")
        
        # Remove from blacklist
        self.db.remove_from_blacklist(blacklist[0]["id"])
        blacklist = self.db.get_blacklist()
        self.assertEqual(len(blacklist), 0)
    
    def test_custom_filters(self):
        """Test custom filter operations"""
        filter_id = self.db.add_custom_filter(
            "Test Filter",
            "newsletter.*",
            "regex"
        )
        
        self.assertIsNotNone(filter_id)
        
        filters = self.db.get_custom_filters()
        self.assertEqual(len(filters), 1)
        self.assertEqual(filters[0]["name"], "Test Filter")
    
    def test_operation_history(self):
        """Test logging operations"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test",
            received_date=datetime.now()
        )
        
        self.db.log_operation("scan", email_id, "success", "Test operation")
        
        history = self.db.get_recent_operations(10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["operation_type"], "scan")
        self.assertEqual(history[0]["status"], "success")
    
    def test_mark_email_processed(self):
        """Test marking email as processed"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test",
            received_date=datetime.now()
        )
        
        self.db.mark_email_processed(email_id, True)
        
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT processed, has_unsubscribe_link FROM emails WHERE id = ?", (email_id,))
        result = cursor.fetchone()
        
        self.assertEqual(result[0], 1)  # processed = True
        self.assertEqual(result[1], 1)  # has_unsubscribe_link = True
    
    def test_update_email_category(self):
        """Test updating email category"""
        email_id = self.db.add_email(
            message_id="test123",
            sender="test@example.com",
            subject="Test",
            received_date=datetime.now(),
            category="uncategorized"
        )
        
        self.db.update_email_category(email_id, "newsletter")
        
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT category FROM emails WHERE id = ?", (email_id,))
        result = cursor.fetchone()
        
        self.assertEqual(result[0], "newsletter")
    
    def test_settings_operations(self):
        """Test settings get and set"""
        self.db.set_setting("test_key", "test_value")
        
        value = self.db.get_setting("test_key")
        self.assertEqual(value, "test_value")
        
        # Test non-existent setting
        value = self.db.get_setting("nonexistent")
        self.assertIsNone(value)
    
    def test_statistics(self):
        """Test statistics generation"""
        # Add some test data
        email_id1 = self.db.add_email(
            message_id="test1",
            sender="test1@example.com",
            subject="Test 1",
            received_date=datetime.now(),
            category="newsletter"
        )
        self.db.mark_email_processed(email_id1, True)
        
        email_id2 = self.db.add_email(
            message_id="test2",
            sender="test2@example.com",
            subject="Test 2",
            received_date=datetime.now(),
            category="promotion"
        )
        self.db.mark_email_processed(email_id2, True)
        
        link_id1 = self.db.add_unsubscribe_link(email_id1, "https://example.com/unsub1")
        self.db.update_link_status(link_id1, True, 200, None)
        
        link_id2 = self.db.add_unsubscribe_link(email_id2, "https://example.com/unsub2")
        self.db.update_link_status(link_id2, True, 404, "Not found")
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats["total_processed"], 2)
        self.assertEqual(stats["emails_with_links"], 2)
        self.assertEqual(stats["links_clicked"], 2)
        self.assertEqual(stats["successful_clicks"], 1)
        self.assertIn("newsletter", stats["category_breakdown"])
        self.assertIn("promotion", stats["category_breakdown"])


if __name__ == "__main__":
    unittest.main()
