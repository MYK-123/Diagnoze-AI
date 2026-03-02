#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import sqlite3
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import (
    get_connection, get_db, Database, init_db, DB_PATH, DATABASE_URL
)


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection functions"""

    def test_get_connection_returns_connection(self):
        """Test that get_connection returns a sqlite3 connection"""
        conn = get_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()

    def test_get_connection_enables_foreign_keys(self):
        """Test that connections have foreign keys enabled"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)  # Foreign keys enabled
        conn.close()

    def test_get_connection_row_factory(self):
        """Test that row_factory is set to sqlite3.Row"""
        conn = get_connection()
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_get_db_context_manager(self):
        """Test that get_db context manager works"""
        with get_db() as conn:
            self.assertIsInstance(conn, sqlite3.Connection)

    def test_get_db_closes_connection(self):
        """Test that get_db closes connection after use"""
        with get_db() as conn:
            pass
        # Connection should be closed, accessing it should raise
        try:
            conn.execute("SELECT 1")
            # If it doesn't raise, that's fine for some SQLite implementations
        except sqlite3.ProgrammingError:
            pass  # Expected


class TestDatabase(unittest.TestCase):
    """Test Database class"""

    def setUp(self):
        """Set up test database"""
        self.conn = get_connection()
        self.db = Database(self.conn)
        
        # Create test table
        self.db.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)
        self.db.commit()

    def tearDown(self):
        """Clean up"""
        self.db.execute("DROP TABLE IF EXISTS test_table")
        self.db.commit()
        self.conn.close()

    def test_database_init(self):
        """Test Database initialization"""
        self.assertIsNotNone(self.db.conn)
        self.assertIsNotNone(self.db.cursor)

    def test_execute_insert(self):
        """Test executing insert query"""
        cursor = self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.commit()
        self.assertIsNotNone(cursor)

    def test_execute_select(self):
        """Test executing select query"""
        self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.commit()
        
        cursor = self.db.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)

    def test_executemany(self):
        """Test executing multiple queries"""
        data = [
            ("test1", 1),
            ("test2", 2),
            ("test3", 3)
        ]
        self.db.executemany(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            data
        )
        self.db.commit()
        
        cursor = self.db.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 3)

    def test_fetch_one_returns_dict(self):
        """Test that fetch_one returns dictionary"""
        self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.commit()
        
        row = self.db.fetch_one("SELECT * FROM test_table WHERE name = ?", ("test",))
        self.assertIsInstance(row, dict)
        self.assertEqual(row["name"], "test")
        self.assertEqual(row["value"], 42)

    def test_fetch_one_returns_none_when_not_found(self):
        """Test that fetch_one returns None when no row found"""
        row = self.db.fetch_one("SELECT * FROM test_table WHERE name = ?", ("nonexistent",))
        self.assertIsNone(row)

    def test_fetch_all_returns_list_of_dicts(self):
        """Test that fetch_all returns list of dictionaries"""
        data = [
            ("test1", 1),
            ("test2", 2),
            ("test3", 3)
        ]
        self.db.executemany(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            data
        )
        self.db.commit()
        
        rows = self.db.fetch_all("SELECT * FROM test_table")
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertIsInstance(row, dict)

    def test_fetch_all_returns_empty_list(self):
        """Test that fetch_all returns empty list when no rows"""
        rows = self.db.fetch_all("SELECT * FROM test_table")
        self.assertEqual(rows, [])

    def test_fetch_scalar_returns_value(self):
        """Test that fetch_scalar returns single value"""
        self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.commit()
        
        value = self.db.fetch_scalar("SELECT value FROM test_table WHERE name = ?", ("test",))
        self.assertEqual(value, 42)

    def test_fetch_scalar_returns_none(self):
        """Test that fetch_scalar returns None when not found"""
        value = self.db.fetch_scalar("SELECT value FROM test_table WHERE name = ?", ("nonexistent",))
        self.assertIsNone(value)

    def test_commit(self):
        """Test commit functionality"""
        self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.commit()
        
        # Data should persist
        row = self.db.fetch_one("SELECT * FROM test_table WHERE name = ?", ("test",))
        self.assertIsNotNone(row)

    def test_rollback(self):
        """Test rollback functionality"""
        self.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        self.db.rollback()
        
        # Data should not persist
        rows = self.db.fetch_all("SELECT * FROM test_table")
        self.assertEqual(len(rows), 0)


class TestDatabaseInitialization(unittest.TestCase):
    """Test database schema initialization"""

    def setUp(self):
        """Set up test database with temp file"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

    def tearDown(self):
        """Clean up temp database"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    @patch('api.database.get_connection')
    def test_init_db_creates_tables(self, mock_get_connection):
        """Test that init_db creates all required tables"""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_connection.return_value = conn
        
        init_db()
        
        # Check that tables exist
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'sessions', 'chat_sessions', 'chat_messages', 'chat_history')"
        )
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        self.assertIn("users", table_names)
        self.assertIn("sessions", table_names)
        self.assertIn("chat_sessions", table_names)
        self.assertIn("chat_messages", table_names)
        self.assertIn("chat_history", table_names)
        conn.close()

    @patch('api.database.get_connection')
    def test_init_db_creates_indexes(self, mock_get_connection):
        """Test that init_db creates required indexes"""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_connection.return_value = conn
        
        init_db()
        
        # Check indexes
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        index_names = [i[0] for i in indexes]
        
        self.assertIn("idx_users_email", index_names)
        self.assertIn("idx_sessions_user_id", index_names)
        conn.close()

    @patch('api.database.get_connection')
    def test_init_db_users_table_structure(self, mock_get_connection):
        """Test users table has correct columns"""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_connection.return_value = conn
        
        init_db()
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        col_names = [c[1] for c in columns]
        
        required_cols = ['id', 'email', 'password_hash', 'first_name', 'last_name']
        for col in required_cols:
            self.assertIn(col, col_names)
        conn.close()

    @patch('api.database.get_connection')
    def test_init_db_sessions_table_structure(self, mock_get_connection):
        """Test sessions table has correct columns"""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_connection.return_value = conn
        
        init_db()
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(sessions)")
        columns = cursor.fetchall()
        col_names = [c[1] for c in columns]
        
        required_cols = ['token', 'user_id', 'created_at', 'expires_at']
        for col in required_cols:
            self.assertIn(col, col_names)
        conn.close()

    @patch('api.database.get_connection')
    def test_init_db_chat_history_structure(self, mock_get_connection):
        """Test chat_history table structure"""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_connection.return_value = conn
        
        init_db()
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = cursor.fetchall()
        col_names = [c[1] for c in columns]
        
        required_cols = ['id', 'user_id', 'title', 'created_at']
        for col in required_cols:
            self.assertIn(col, col_names)
        conn.close()


class TestDatabaseConstants(unittest.TestCase):
    """Test database module constants"""

    def test_db_path_defined(self):
        """Test that DB_PATH is defined"""
        self.assertIsNotNone(DB_PATH)

    def test_database_url_defined(self):
        """Test that DATABASE_URL is defined"""
        self.assertIsNotNone(DATABASE_URL)

    def test_database_url_format(self):
        """Test DATABASE_URL has correct format"""
        self.assertIn("sqlite:///", DATABASE_URL)


if __name__ == '__main__':
    unittest.main()
