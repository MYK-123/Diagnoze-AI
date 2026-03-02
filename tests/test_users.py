#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.users import (
    User, check_auth_info, add_user_to_db,
    update_user_role, delete_user, get_user_by_id,
    ROLE_USER, ROLE_MEDICAL_STUDENT, ROLE_ADMIN
)


class TestUser(unittest.TestCase):
    """Test the User entity class"""

    def setUp(self):
        self.user = User(1, "testuser", "test@example.com", ROLE_USER)

    def test_user_init(self):
        """Test user initialization"""
        self.assertEqual(self.user.user_id, 1)
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.role, ROLE_USER)

    def test_user_attributes(self):
        """Test user attributes"""
        self.assertEqual(self.user.user_id, 1)
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.role, ROLE_USER)

    def test_user_different_roles(self):
        """Test user with different roles"""
        user_student = User(2, "student", "student@example.com", ROLE_MEDICAL_STUDENT)
        user_admin = User(3, "admin", "admin@example.com", ROLE_ADMIN)

        self.assertEqual(user_student.role, ROLE_MEDICAL_STUDENT)
        self.assertEqual(user_admin.role, ROLE_ADMIN)


class TestUserAuthentication(unittest.TestCase):
    """Test user authentication functions"""

    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_success(self, mock_get_db):
        """Test successful authentication"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com", ROLE_USER)

        user = check_auth_info("testuser", "hashed_password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")

    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_failure(self, mock_get_db):
        """Test failed authentication"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user = check_auth_info("testuser", "wrong_password")
        self.assertIsNone(user)

    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_exception(self, mock_get_db):
        """Test authentication with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            user = check_auth_info("testuser", "password")
        self.assertIsNone(user)

    @patch('auth.users.coredb.getDBObject')
    def test_add_user_to_db_success(self, mock_get_db):
        """Test adding user to database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success = add_user_to_db("newuser", "new@example.com", "hashed_password")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('auth.users.coredb.getDBObject')
    def test_add_user_to_db_exception(self, mock_get_db):
        """Test adding user with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_user_to_db("newuser", "new@example.com", "hashed_password")
        self.assertFalse(success)
        mock_conn.rollback.assert_called_once()

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_success(self, mock_get_db):
        """Test updating user role"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success = update_user_role(1, ROLE_ADMIN)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_invalid_role(self, mock_get_db):
        """Test updating user with invalid role"""
        success = update_user_role(1, "invalid_role")
        self.assertFalse(success)

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_exception(self, mock_get_db):
        """Test updating role with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = update_user_role(1, ROLE_ADMIN)
        self.assertFalse(success)

    @patch('auth.users.coredb.getDBObject')
    def test_delete_user_success(self, mock_get_db):
        """Test deleting user"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success = delete_user(1)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('auth.users.coredb.getDBObject')
    def test_delete_user_exception(self, mock_get_db):
        """Test deleting user with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = delete_user(1)
        self.assertFalse(success)

    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_success(self, mock_get_db):
        """Test getting user by ID"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com", ROLE_USER)

        user = get_user_by_id(1)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_not_found(self, mock_get_db):
        """Test getting non-existent user"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user = get_user_by_id(999)
        self.assertIsNone(user)

    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_exception(self, mock_get_db):
        """Test getting user with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            user = get_user_by_id(1)
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()
