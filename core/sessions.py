#!/bin/env python3

import uuid

from db import __core_db__ as coredb

def create_session(user_id: int) -> str:
    """
    Create a new session for the given user ID.
    Returns - session token
    """
    session_token = str(uuid.uuid4())
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_session (token, user_id) VALUES (?, ?)",
            (session_token, user_id)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        conn.close()
    
    return session_token

def validate_session(session_token: str, user_id: int) -> bool:
    """
    Validate the given session token for the user.
    Returns - True if valid, False otherwise
    """
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM user_session WHERE token = ? AND user_id = ?",
            (session_token, user_id)
            )
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0
    except Exception as e:
        print(f"Error validating session: {e}")
        conn.close()
        return False

def destroy_session(session_token: str) -> bool:
    """
    Destroy the given session token.
    """

    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_session WHERE token = ?",
            (session_token,)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error destroying session: {e}")
        conn.rollback()
        conn.close()
        return False

def get_user_id_from_session(session_token: str) -> int | None:
    """
    Retrieve the user ID associated with the given session token.
    Returns - user ID or None if session is invalid
    """
    
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM user_session WHERE token = ?",
            (session_token,)
            )
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"Error retrieving user ID from session: {e}")
        conn.close()
        return None
