from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .db_models import SessionToken, User


security = HTTPBearer()


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
    try:
        scheme, iter_s, salt_hex, hash_hex = stored.split("$", 3)
        if scheme != "pbkdf2":
            return False
        computed = hash_password(password, salt=salt_hex)
        return hmac.compare_digest(computed, stored)
    except Exception:
        return False


def create_session(db: Session, user: User, minutes: int = 30) -> SessionToken:
    token = SessionToken.new_token()
    session = SessionToken(
        token=token,
        user_id=user.id,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=minutes),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    print(f"CREATED SESSION: {token}")  # DEBUG
    return session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    token = credentials.credentials
    print(f"RECEIVED TOKEN: {token}")  # DEBUG
    session = db.get(SessionToken, token)
    print(f"DB SESSION LOOKUP: {session}")  # DEBUG
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    if session.expires_at < datetime.utcnow():
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Return dict to preserve existing router expectations
    return user.to_public_dict()


async def get_current_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("account_type") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

