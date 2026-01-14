"""Database models for email unsubscribe automation"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import os


class Database:
    """Main database class for managing email operations"""
    
    def __init__(self, db_path: str = "email_automation.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.create_tables()
    
    def connect(self):
        """Create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Create all necessary tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Email table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                sender TEXT NOT NULL,
                subject TEXT,
                received_date TIMESTAMP,
                category TEXT DEFAULT 'uncategorized',
                has_unsubscribe_link BOOLEAN DEFAULT 0,
                processed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Unsubscribe links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unsubscribe_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                link TEXT NOT NULL,
                clicked BOOLEAN DEFAULT 0,
                click_timestamp TIMESTAMP,
                status_code INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        """)
        
        # Whitelist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_pattern TEXT UNIQUE NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Blacklist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_pattern TEXT UNIQUE NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Custom filters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pattern TEXT NOT NULL,
                filter_type TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Operation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                email_id INTEGER,
                status TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def add_email(self, message_id: str, sender: str, subject: str, 
                  received_date: datetime, category: str = "uncategorized") -> int:
        """Add an email record"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO emails (message_id, sender, subject, received_date, category)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, sender, subject, received_date, category))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Email already exists, return existing ID
            cursor.execute("SELECT id FROM emails WHERE message_id = ?", (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_unsubscribe_link(self, email_id: int, link: str) -> int:
        """Add an unsubscribe link"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO unsubscribe_links (email_id, link)
            VALUES (?, ?)
        """, (email_id, link))
        conn.commit()
        return cursor.lastrowid
    
    def update_link_status(self, link_id: int, clicked: bool, status_code: int = None, 
                          error_message: str = None):
        """Update the status of an unsubscribe link"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE unsubscribe_links 
            SET clicked = ?, click_timestamp = ?, status_code = ?, error_message = ?
            WHERE id = ?
        """, (clicked, datetime.now(), status_code, error_message, link_id))
        conn.commit()
    
    def add_to_whitelist(self, email_pattern: str, notes: str = None):
        """Add an email pattern to whitelist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO whitelist (email_pattern, notes)
                VALUES (?, ?)
            """, (email_pattern, notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def add_to_blacklist(self, email_pattern: str, notes: str = None):
        """Add an email pattern to blacklist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO blacklist (email_pattern, notes)
                VALUES (?, ?)
            """, (email_pattern, notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_whitelist(self) -> List[Dict]:
        """Get all whitelist entries"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM whitelist ORDER BY added_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_blacklist(self) -> List[Dict]:
        """Get all blacklist entries"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM blacklist ORDER BY added_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def remove_from_whitelist(self, pattern_id: int):
        """Remove entry from whitelist"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM whitelist WHERE id = ?", (pattern_id,))
        conn.commit()
    
    def remove_from_blacklist(self, pattern_id: int):
        """Remove entry from blacklist"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blacklist WHERE id = ?", (pattern_id,))
        conn.commit()
    
    def add_custom_filter(self, name: str, pattern: str, filter_type: str) -> int:
        """Add a custom filter"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO custom_filters (name, pattern, filter_type)
            VALUES (?, ?, ?)
        """, (name, pattern, filter_type))
        conn.commit()
        return cursor.lastrowid
    
    def get_custom_filters(self) -> List[Dict]:
        """Get all custom filters"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM custom_filters WHERE enabled = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def log_operation(self, operation_type: str, email_id: int = None, 
                     status: str = "success", details: str = None):
        """Log an operation to history"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO operation_history (operation_type, email_id, status, details)
            VALUES (?, ?, ?, ?)
        """, (operation_type, email_id, status, details))
        conn.commit()
    
    def get_statistics(self) -> Dict:
        """Get statistics about email operations"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total emails processed
        cursor.execute("SELECT COUNT(*) FROM emails WHERE processed = 1")
        stats['total_processed'] = cursor.fetchone()[0]
        
        # Total emails with unsubscribe links
        cursor.execute("SELECT COUNT(*) FROM emails WHERE has_unsubscribe_link = 1")
        stats['emails_with_links'] = cursor.fetchone()[0]
        
        # Total links clicked
        cursor.execute("SELECT COUNT(*) FROM unsubscribe_links WHERE clicked = 1")
        stats['links_clicked'] = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("""
            SELECT COUNT(*) FROM unsubscribe_links 
            WHERE clicked = 1 AND status_code BETWEEN 200 AND 299
        """)
        stats['successful_clicks'] = cursor.fetchone()[0]
        
        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM emails 
            GROUP BY category
        """)
        stats['category_breakdown'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats
    
    def get_recent_operations(self, limit: int = 50) -> List[Dict]:
        """Get recent operations"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM operation_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_unprocessed_emails(self) -> List[Dict]:
        """Get unprocessed emails"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM emails 
            WHERE processed = 0 
            ORDER BY received_date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_email_processed(self, email_id: int, has_unsubscribe: bool = False):
        """Mark an email as processed"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE emails 
            SET processed = 1, has_unsubscribe_link = ?
            WHERE id = ?
        """, (has_unsubscribe, email_id))
        conn.commit()
    
    def update_email_category(self, email_id: int, category: str):
        """Update email category"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE emails 
            SET category = ?
            WHERE id = ?
        """, (category, email_id))
        conn.commit()
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        conn.commit()
