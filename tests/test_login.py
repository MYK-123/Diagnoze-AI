#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.login import (
    authenticate, create_new_user, delete_user,
    update_user_role, get_user_from_session,
    logout_user, login_user, is_session_valid
)
from auth.users import User, ROLE_USER, ROLE_ADMIN


class TestLogin(unittest.TestCase):
    """Test login and authentication functions"""

    @patch('auth.login.check_auth_info')
    def test_authenticate_success(self, mock_check_auth):
        """Test successful authentication"""
        mock_user = User(1, "testuser", "test@example.com", ROLE_USER)
        mock_check_auth.return_value = mock_user

        success, result = authenticate("testuser", "password")
        self.assertTrue(success)
        self.assertEqual(result.username, "testuser")

    @patch('auth.login.check_auth_info')
    def test_authenticate_failure(self, mock_check_auth):
        """Test failed authentication"""
        mock_check_auth.return_value = None

        success, result = authenticate("testuser", "wrong_password")
        self.assertFalse(success)
        self.assertEqual(result, "Invalid username or password")

    @patch('auth.login.add_user_to_db')
    def test_create_new_user_success(self, mock_add_user):
        """Test creating a new user"""
        mock_add_user.return_value = True

        success, message = create_new_user("newuser", "new@example.com", "password")
        self.assertTrue(success)
        self.assertEqual(message, "User created successfully")

    @patch('auth.login.add_user_to_db')
    def test_create_new_user_failure(self, mock_add_user):
        """Test creating user with failure"""
        mock_add_user.return_value = False

        success, message = create_new_user("newuser", "new@example.com", "password")
        self.assertFalse(success)
        self.assertEqual(message, "Failed to create user")

    @patch('auth.login.delete_user_core')
    def test_delete_user(self, mock_delete):
        """Test deleting a user"""
        mock_delete.return_value = True

        success = delete_user(1)
        self.assertTrue(success)

    @patch('auth.login.update_user_role_core')
    def test_update_user_role(self, mock_update_role):
        """Test updating user role"""
        mock_update_role.return_value = True

        success = update_user_role(1, ROLE_ADMIN)
        self.assertTrue(success)

    @patch('auth.login.get_user_by_id')
    @patch('auth.login.get_user_id_from_session')
    def test_get_user_from_session_valid(self, mock_get_user_id, mock_get_user):
        """Test getting user from valid session"""
        mock_get_user_id.return_value = 1
        mock_user = User(1, "testuser", "test@example.com", ROLE_USER)
        mock_get_user.return_value = mock_user

        user = get_user_from_session("valid-token")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    @patch('auth.login.get_user_id_from_session')
    def test_get_user_from_session_invalid(self, mock_get_user_id):
        """Test getting user from invalid session"""
        mock_get_user_id.return_value = None

        user = get_user_from_session("invalid-token")
        self.assertIsNone(user)

    @patch('auth.login.destroy_session')
    def test_logout_user(self, mock_destroy):
        """Test logging out user"""
        mock_destroy.return_value = True

        success = logout_user("test-token")
        self.assertTrue(success)

    @patch('auth.login.create_session')
    @patch('auth.login.check_auth_info')
    def test_login_user_success(self, mock_check_auth, mock_create_session):
        """Test successful user login"""
        mock_user = User(1, "testuser", "test@example.com", ROLE_USER)
        mock_check_auth.return_value = mock_user
        mock_create_session.return_value = "test-token"

        success, token, user = login_user("testuser", "password")
        self.assertTrue(success)
        self.assertEqual(token, "test-token")
        self.assertEqual(user.username, "testuser")

    @patch('auth.login.check_auth_info')
    def test_login_user_invalid_credentials(self, mock_check_auth):
        """Test login with invalid credentials"""
        mock_check_auth.return_value = None

        success, message, user = login_user("testuser", "wrong_password")
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username or password")
        self.assertIsNone(user)

    @patch('auth.login.create_session')
    @patch('auth.login.check_auth_info')
    def test_login_user_session_creation_failure(self, mock_check_auth, mock_create_session):
        """Test login when session creation fails"""
        mock_user = User(1, "testuser", "test@example.com", ROLE_USER)
        mock_check_auth.return_value = mock_user
        mock_create_session.return_value = None

        success, message, user = login_user("testuser", "password")
        self.assertFalse(success)
        self.assertEqual(message, "Failed to create session")
        self.assertIsNone(user)

    @patch('auth.login.validate_session')
    def test_is_session_valid_true(self, mock_validate):
        """Test session validation returns true"""
        mock_validate.return_value = True

        result = is_session_valid("test-token", 1)
        self.assertTrue(result)

    @patch('auth.login.validate_session')
    def test_is_session_valid_false(self, mock_validate):
        """Test session validation returns false"""
        mock_validate.return_value = False

        result = is_session_valid("invalid-token", 1)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
