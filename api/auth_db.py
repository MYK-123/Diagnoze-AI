from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.core import get_db
from .database import Database
from .db_models import SessionToken, User

security = HTTPBearer()

# Configure module logger
logger = logging.getLogger("diagnoze.auth_db")

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    PBKDF2-HMAC-SHA256 password hashing.
    Format: pbkdf2$<iterations>$<salt_hex>$<hash_hex>
    """
    iterations = 120_000
    salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return f"pbkdf2${iterations}${salt_bytes.hex()}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash"""
    try:
        scheme, iter_s, salt_hex, hash_hex = stored.split("$", 3)
        if scheme != "pbkdf2":
            return False
        computed = hash_password(password, salt=salt_hex)
        return hmac.compare_digest(computed, stored)
    except Exception:
        return False

def create_session(conn: sqlite3.Connection, user: User, minutes: int = 30) -> SessionToken:
    """Create a new session token"""
    db = Database(conn)
    token = SessionToken.new_token()
    now = datetime.utcnow()
    expires_at = (now + timedelta(minutes=minutes)).isoformat()
    
    db.execute(
        """
        INSERT INTO user_session (token, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (token, user.user_id, now.isoformat(), expires_at)
    )
    db.commit()
    
    session = SessionToken(
        token=token,
        user_id=user.user_id,
        username=user.username,
        created_at=now.isoformat(),
        expires_at=expires_at,
    )
    logger.info("Created session token=%s for user_id=%s", token, user.user_id)
    return session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Get current authenticated user from token"""
    logger.debug("Checking current user")
    token = None
    try:
        token = credentials.credentials
    except Exception:
        logger.debug("No credentials provided in request")

    logger.info("Received token: %s", token)
    db = Database(conn)
    logger.debug("Querying user_session for token")
    session_row = db.fetch_one("SELECT * FROM user_session WHERE token = ?", (token,))
    logger.info("DB session lookup result: %s", session_row)
    
    if not session_row:
        logger.warning("Invalid or expired token: %s", token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    session = SessionToken.from_db_row(session_row)
    
    # Check expiration
    if  session.expires_at is not None and datetime.fromisoformat(session.expires_at) < datetime.utcnow():
        db.execute("DELETE FROM user_session WHERE token = ?", (token,))
        db.commit()
        logger.warning("Session expired and removed for token=%s", token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    
    # Get user
    user_row = db.fetch_one("SELECT * FROM users WHERE user_id = ?", (session.user_id,))
    if not user_row:
        logger.error("User not found for session user_id=%s", session.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    user = User.from_db_row(user_row)
    if not user.is_active:
        logger.warning("Inactive user attempted access: user_id=%s", user.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Return dict to preserve existing router expectations
    logger.info("Authenticated user_id=%s", user.user_id)
    return user.to_public_dict()

async def get_current_admin(user: dict = Depends(get_current_user)) -> dict:
    """Verify user is an admin"""
    if user.get("account_type") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

