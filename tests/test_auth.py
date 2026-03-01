#!/bin/env python3

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock the db module before importing
sys.modules['db'] = MagicMock()
sys.modules['db.core'] = MagicMock()

from auth.users import (
    User,
    check_auth_info,
    add_user_to_db,
    update_user_role,
    delete_user,
    get_user_by_id,
    ROLE_USER,
    ROLE_MEDICAL_STUDENT,
    ROLE_ADMIN
)
from auth import login as auth_module
from tests.test_db import init_db, getDBObject

# We'll use a test user
TEST_USERNAME = "test_user"
TEST_EMAIL = "test_user@example.com"
TEST_PASSWORD = "securepassword123"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Initialize the test database
    init_db()
    # Reset tables before tests
    def resetTables():
        conn = getDBObject()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM user_session")
        conn.commit()
        conn.close()
    resetTables()
    yield
    # Optionally reset again after all tests
    resetTables()

@pytest.fixture(scope="module")
def create_test_user():
    # Create a new user
    success, msg = auth_module.create_new_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
    assert success, f"Failed to create test user: {msg}"
    yield  # allow tests to run
    # Cleanup: delete user after tests
    user = auth_module.authenticate(TEST_USERNAME, TEST_PASSWORD)[1]
    if isinstance(user, User):
        auth_module.delete_user(user.user_id)

def test_authenticate_success(create_test_user):
    success, user_or_msg = auth_module.authenticate(TEST_USERNAME, TEST_PASSWORD)
    assert success
    assert isinstance(user_or_msg, User)
    assert user_or_msg.username == TEST_USERNAME

def test_authenticate_failure(create_test_user):
    success, msg = auth_module.authenticate(TEST_USERNAME, "wrongpassword")
    assert not success
    assert msg == "Invalid username or password"

def test_login_and_session(create_test_user):
    # Login
    success, session_token, user = auth_module.login_user(TEST_USERNAME, TEST_PASSWORD)
    assert success
    assert isinstance(user, User)
    assert session_token is not None

    # Session validation
    is_valid = auth_module.is_session_valid(session_token, user.user_id)
    assert is_valid

    # Logout
    logout_success = auth_module.logout_user(session_token)
    assert logout_success

    # Session should now be invalid
    is_valid_after_logout = auth_module.is_session_valid(session_token, user.user_id)
    assert not is_valid_after_logout

def test_update_user_role(create_test_user):
    user = auth_module.authenticate(TEST_USERNAME, TEST_PASSWORD)[1]
    assert isinstance(user, User)
    
    # Update role
    success = auth_module.update_user_role(user.user_id, "admin")
    assert success
    
    # Fetch user and check role
    updated_user = auth_module.get_user_from_session(auth_module.create_session(user.user_id))
    assert updated_user is not None
    assert updated_user.role == "admin"


class TestUserClass:
    """Tests for User class"""
    
    def test_user_creation(self):
        """Test creating a user object"""
        user = User(uid=1, username="john_doe", email="john@example.com", role="user")
        
        assert user.user_id == 1
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.role == "user"

    def test_user_attributes(self):
        """Test user object attributes"""
        user = User(uid=2, username="jane_smith", email="jane@example.com", role="admin")
        
        assert user.user_id == 2
        assert user.username == "jane_smith"
        assert user.email == "jane@example.com"
        assert user.role == "admin"


class TestCheckAuthInfo:
    """Tests for check_auth_info function"""
    
    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_success(self, mock_get_db):
        """Test successful authentication"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "john_doe", "john@example.com", "user")
        
        result = check_auth_info("john_doe", "hashed_password")
        
        assert result is not None
        assert isinstance(result, User)
        assert result.user_id == 1
        assert result.username == "john_doe"

    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_invalid_credentials(self, mock_get_db):
        """Test authentication with invalid credentials"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = check_auth_info("invalid_user", "wrong_password")
        
        assert result is None

    @patch('auth.users.coredb.getDBObject')
    def test_check_auth_info_exception(self, mock_get_db):
        """Test authentication with database exception"""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.side_effect = Exception("Database error")
        
        result = check_auth_info("user", "password")
        
        assert result is None
        assert mock_conn.close.called


class TestAddUserToDb:
    """Tests for add_user_to_db function"""
    
    @patch('auth.users.coredb.getDBObject')
    def test_add_user_success(self, mock_get_db):
        """Test successful user addition"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = add_user_to_db("new_user", "new@example.com", "hashed_password")
        
        assert result is True
        assert mock_conn.commit.called
        assert mock_cursor.execute.called

    @patch('auth.users.coredb.getDBObject')
    def test_add_user_exception(self, mock_get_db):
        """Test user addition with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = add_user_to_db("user", "email@example.com", "password")
        
        assert result is False
        assert mock_conn.rollback.called

    @patch('auth.users.coredb.getDBObject')
    def test_add_user_inserts_correct_values(self, mock_get_db):
        """Test that correct values are inserted"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        add_user_to_db("testuser", "test@example.com", "hash123")
        
        call_args = mock_cursor.execute.call_args
        assert "testuser" in call_args[0] or "testuser" in str(call_args[1])
        assert "test@example.com" in call_args[0] or "test@example.com" in str(call_args[1])


class TestUpdateUserRole:
    """Tests for update_user_role function"""
    
    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_success(self, mock_get_db):
        """Test successful role update"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = update_user_role(1, ROLE_ADMIN)
        
        assert result is True
        assert mock_conn.commit.called

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_invalid_role(self, mock_get_db):
        """Test role update with invalid role"""
        result = update_user_role(1, "invalid_role")
        
        assert result is False
        assert not mock_get_db.called

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_medical_student(self, mock_get_db):
        """Test updating user to medical student role"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = update_user_role(2, ROLE_MEDICAL_STUDENT)
        
        assert result is True

    @patch('auth.users.coredb.getDBObject')
    def test_update_user_role_exception(self, mock_get_db):
        """Test role update with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = update_user_role(1, ROLE_USER)
        
        assert result is False
        assert mock_conn.rollback.called


class TestDeleteUser:
    """Tests for delete_user function"""
    
    @patch('auth.users.coredb.getDBObject')
    def test_delete_user_success(self, mock_get_db):
        """Test successful user deletion"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        result = delete_user(1)
        
        assert result is True
        assert mock_conn.commit.called

    @patch('auth.users.coredb.getDBObject')
    def test_delete_user_exception(self, mock_get_db):
        """Test user deletion with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = delete_user(1)
        
        assert result is False
        assert mock_conn.rollback.called


class TestGetUserById:
    """Tests for get_user_by_id function"""
    
    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_success(self, mock_get_db):
        """Test successful user retrieval"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "john_doe", "john@example.com", "user")
        
        result = get_user_by_id(1)
        
        assert result is not None
        assert isinstance(result, User)
        assert result.user_id == 1
        assert result.username == "john_doe"

    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_not_found(self, mock_get_db):
        """Test user retrieval when user doesn't exist"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = get_user_by_id(999)
        
        assert result is None

    @patch('auth.users.coredb.getDBObject')
    def test_get_user_by_id_exception(self, mock_get_db):
        """Test user retrieval with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = get_user_by_id(1)
        
        assert result is None
        assert mock_conn.close.called


class TestRoleConstants:
    """Tests for role constants"""
    
    def test_role_user_constant(self):
        """Test ROLE_USER constant"""
        assert ROLE_USER == "user"

    def test_role_medical_student_constant(self):
        """Test ROLE_MEDICAL_STUDENT constant"""
        assert ROLE_MEDICAL_STUDENT == "medical_student"

    def test_role_admin_constant(self):
        """Test ROLE_ADMIN constant"""
        assert ROLE_ADMIN == "admin"

    def test_valid_roles_set(self):
        """Test that all valid roles are properly defined"""
        valid_roles = [ROLE_USER, ROLE_MEDICAL_STUDENT, ROLE_ADMIN]
        assert len(valid_roles) == 3
        assert len(set(valid_roles)) == 3  # All unique
