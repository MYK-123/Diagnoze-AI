#!/bin/env python3

import pytest
from core.users import User
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
