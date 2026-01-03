#!/bin/env python3

from core.users import User
from core.users import check_auth_info
from core.users import add_user_to_db
from core.users import update_user_role as update_user_role_core
from core.users import delete_user as delete_user_core
from core.users import get_user_by_id

from core.sessions import create_session
from core.sessions import validate_session
from core.sessions import get_user_id_from_session
from core.sessions import destroy_session

def authenticate(username, password) -> tuple[bool, User | str]:
    """
    Handle user login process.
    Returns - success status and user information or error message
    """

    user = check_auth_info(username, password)
    if user:
        return True, user
    else:
        return False, "Invalid username or password"


def create_new_user(username, email, password) -> tuple[bool, str]:
    """
    Handle new user registration process.
    Returns - success status and message
    """
    success = add_user_to_db(username, email, password)
    if not success:
        return False, "Failed to create user"
    return True, "User created successfully"

def delete_user(user_id: int) -> bool:
    """
    Handle user deletion process.
    Returns - success status
    """
    success = delete_user_core(user_id)
    return success

def update_user_role(user_id: int, new_role: str) -> bool:
    """
    Handle user role update process.
    Returns - success status
    """
    success = update_user_role_core(user_id, new_role)
    return success

def get_user_from_session(session_token: str) -> User | None:
    """
    Retrieve user information from session token.
    Returns - User object or None if session is invalid
    """
    user_id = get_user_id_from_session(session_token)
    if user_id is None:
        return None
    user = get_user_by_id(user_id)
    return user

def logout_user(session_token: str) -> bool:
    """
    Handle user logout process.
    Returns - success status
    """
    success = destroy_session(session_token)
    return success

def login_user(username: str, password: str) -> tuple[bool, str, User]:
    """
    Handle user login process.
    Returns - success status and session token or error message
    """
    success, user_or_msg = authenticate(username, password)
    if not success:
        msg:str = user_or_msg  # type: ignore
        return False, msg, None

    user: User = user_or_msg  # type: ignore
    session_token = create_session(user.user_id)
    if not session_token:
        return False, "Failed to create session", None

    return True, session_token, user

def is_session_valid(session_token: str, user_id: int) -> bool:
    """
    Validate if the session token is valid for the given user ID.
    Returns - True if valid, False otherwise
    """
    return validate_session(session_token, user_id)

