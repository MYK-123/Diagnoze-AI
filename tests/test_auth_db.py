#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
import hmac

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.auth_db import (
    hash_password, verify_password, create_session, get_current_user, 
    get_current_admin
)
from api.db_models import User, SessionToken


class TestPasswordHashing(unittest.TestCase):
    """Test password hashing functions"""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        hashed = hash_password("mypassword")
        self.assertIsInstance(hashed, str)

    def test_hash_password_has_correct_format(self):
        """Test that hashed password has correct format"""
        hashed = hash_password("mypassword")
        parts = hashed.split("$")
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "pbkdf2")

    def test_hash_password_generates_salt(self):
        """Test that hash_password generates different salts"""
        hash1 = hash_password("password")
        hash2 = hash_password("password")
        # Different salts should generate different hashes
        self.assertNotEqual(hash1, hash2)

    def test_hash_password_with_provided_salt(self):
        """Test hash_password with provided salt"""
        salt = "a1b2c3d4e5f6g7h8"
        hash1 = hash_password("password", salt=salt)
        hash2 = hash_password("password", salt=salt)
        # Same salt should generate same hash
        self.assertEqual(hash1, hash2)

    def test_hash_password_includes_iterations(self):
        """Test that hash contains iterations"""
        hashed = hash_password("password")
        parts = hashed.split("$")
        iterations = int(parts[1])
        self.assertEqual(iterations, 120_000)

    def test_verify_password_correct(self):
        """Test verify_password with correct password"""
        hashed = hash_password("mypassword")
        result = verify_password("mypassword", hashed)
        self.assertTrue(result)

    def test_verify_password_incorrect(self):
        """Test verify_password with incorrect password"""
        hashed = hash_password("mypassword")
        result = verify_password("wrongpassword", hashed)
        self.assertFalse(result)

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        hashed = hash_password("MyPassword")
        result = verify_password("mypassword", hashed)
        self.assertFalse(result)

    def test_verify_password_invalid_format(self):
        """Test verify_password with invalid format"""
        result = verify_password("password", "invalid_hash")
        self.assertFalse(result)

    def test_verify_password_wrong_scheme(self):
        """Test verify_password with wrong scheme"""
        hashed = "argon2$iterations$salt$hash"
        result = verify_password("password", hashed)
        self.assertFalse(result)

    def test_verify_password_empty_hash(self):
        """Test verify_password with empty hash"""
        result = verify_password("password", "")
        self.assertFalse(result)

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        self.assertTrue(result)

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters"""
        password = "密码مرحبا"
        hashed = hash_password(password)
        result = verify_password(password, hashed)
        self.assertTrue(result)


class TestCreateSession(unittest.TestCase):
    """Test create_session function"""

    def setUp(self):
        """Set up test database"""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        self.conn.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL DEFAULT 18,
                gender TEXT NOT NULL DEFAULT 'prefer_not_to_say',
                account_type TEXT NOT NULL DEFAULT 'user',
                phone TEXT,
                preferences_json TEXT NOT NULL DEFAULT '{}',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        # Create sessions table
        self.conn.execute("""
            CREATE TABLE sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Clean up"""
        self.conn.close()

    def test_create_session_returns_session_token(self):
        """Test that create_session returns SessionToken"""
        # Create a user
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(self.conn, user)
        
        self.assertIsInstance(session, SessionToken)
        self.assertEqual(session.user_id, "user1")

    def test_create_session_generates_token(self):
        """Test that create_session generates a token"""
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(self.conn, user)
        
        self.assertIsNotNone(session.token)
        self.assertTrue(session.token.startswith("tok_"))

    def test_create_session_sets_expiration(self):
        """Test that create_session sets expiration"""
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(self.conn, user, minutes=30)
        
        self.assertIsNotNone(session.expires_at)

    def test_create_session_stores_in_db(self):
        """Test that create_session stores token in database"""
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(self.conn, user)
        
        # Verify in database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE token = ?", (session.token,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["user_id"], "user1")

    def test_create_session_default_minutes(self):
        """Test create_session with default expiration minutes"""
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        before = datetime.utcnow()
        session = create_session(self.conn, user)  # Default 30 minutes
        after = datetime.utcnow()
        
        expires = datetime.fromisoformat(session.expires_at)
        expected_min = before + timedelta(minutes=29)
        expected_max = after + timedelta(minutes=31)
        
        self.assertGreater(expires, expected_min)
        self.assertLess(expires, expected_max)

    def test_create_session_custom_minutes(self):
        """Test create_session with custom expiration minutes"""
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(self.conn, user, minutes=60)
        
        expires = datetime.fromisoformat(session.expires_at)
        now = datetime.utcnow()
        difference = (expires - now).total_seconds() / 60
        
        # Should be approximately 60 minutes
        self.assertGreater(difference, 59)
        self.assertLess(difference, 61)


class TestGetCurrentUser(unittest.TestCase):
    """Test get_current_user function"""

    def setUp(self):
        """Set up test database"""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self.conn.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL DEFAULT 18,
                gender TEXT NOT NULL DEFAULT 'prefer_not_to_say',
                account_type TEXT NOT NULL DEFAULT 'user',
                phone TEXT,
                preferences_json TEXT NOT NULL DEFAULT '{}',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Clean up"""
        self.conn.close()

    @patch('api.auth_db.get_db')
    async def test_get_current_user_valid_token(self, mock_get_db):
        """Test get_current_user with valid token"""
        mock_get_db.return_value = self.conn
        
        # Create user
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user.id, user.email, user.password_hash, user.first_name, user.last_name,
             user.age, user.gender, user.account_type, user.phone, user.preferences_json,
             user.created_at, user.last_login, 1)
        )
        
        # Create session
        session = create_session(self.conn, user)
        
        # Test get_current_user
        mock_creds = MagicMock()
        mock_creds.credentials = session.token
        
        result = await get_current_user(mock_creds, self.conn)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], "test@example.com")

    @patch('api.auth_db.get_db')
    async def test_get_current_user_invalid_token(self, mock_get_db):
        """Test get_current_user with invalid token"""
        mock_get_db.return_value = self.conn
        
        mock_creds = MagicMock()
        mock_creds.credentials = "invalid_token"
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            await get_current_user(mock_creds, self.conn)

    @patch('api.auth_db.get_db')
    async def test_get_current_user_expired_session(self, mock_get_db):
        """Test get_current_user with expired session"""
        mock_get_db.return_value = self.conn
        
        # Create user
        user = User(
            user_id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user.id, user.email, user.password_hash, user.first_name, user.last_name,
             user.age, user.gender, user.account_type, user.phone, user.preferences_json,
             user.created_at, user.last_login, 1)
        )
        
        # Create expired session
        expired_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
        token = "tok_expired123"
        cursor.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user.id, datetime.utcnow().isoformat(), expired_time)
        )
        self.conn.commit()
        
        mock_creds = MagicMock()
        mock_creds.credentials = token
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            await get_current_user(mock_creds, self.conn)

    @patch('api.auth_db.get_db')
    async def test_get_current_user_inactive_user(self, mock_get_db):
        """Test get_current_user with inactive user"""
        mock_get_db.return_value = self.conn
        
        # Create inactive user
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hashed", "John", "Doe",
             18, "prefer_not_to_say", "user", None, "{}", datetime.utcnow().isoformat(), None, 0)
        )
        
        # Create session
        expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        token = "tok_test123"
        cursor.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, "user1", datetime.utcnow().isoformat(), expires)
        )
        self.conn.commit()
        
        mock_creds = MagicMock()
        mock_creds.credentials = token
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            await get_current_user(mock_creds, self.conn)


class TestGetCurrentAdmin(unittest.TestCase):
    """Test get_current_admin function"""

    @patch('api.auth_db.get_current_user')
    async def test_get_current_admin_valid(self, mock_get_user):
        """Test get_current_admin with admin user"""
        mock_get_user.return_value = {
            "id": "admin1",
            "email": "admin@example.com",
            "account_type": "admin"
        }
        
        result = await get_current_admin(mock_get_user.return_value)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["account_type"], "admin")

    async def test_get_current_admin_non_admin(self):
        """Test get_current_admin with non-admin user"""
        user = {
            "id": "user1",
            "email": "user@example.com",
            "account_type": "user"
        }
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            await get_current_admin(user)

    async def test_get_current_admin_missing_account_type(self):
        """Test get_current_admin with missing account_type"""
        user = {
            "id": "user1",
            "email": "user@example.com"
        }
        
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):
            await get_current_admin(user)


if __name__ == '__main__':
    unittest.main()
