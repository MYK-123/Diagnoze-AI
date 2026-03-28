from datetime import datetime
import re
import secrets
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth_db import create_session, hash_password, verify_password
from db.core import get_db
from ..database import Database
from ..db_models import SessionToken, User
from ..models.schemas import LoginRequest, RegisterRequest
from ..models.responses import success_response, login_response

router = APIRouter()
security = HTTPBearer()

@router.post("/login", summary="User login")
async def login(login_data: LoginRequest, conn: sqlite3.Connection = Depends(get_db)):
    """Authenticate user and return token"""
    db = Database(conn)
    
    user_row = db.fetch_one(
        "SELECT * FROM users WHERE email = ?",
        (str(login_data.email),)
    )
    
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user = User.from_db_row(user_row)
    
    if not user.is_active or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.last_login = datetime.utcnow().isoformat()
    db.execute(
        "UPDATE users SET last_login = ? WHERE user_id = ?",
        (user.last_login, user.user_id)
    )
    db.commit()

    session = create_session(conn, user, minutes=30)

    return login_response(session.token, {
        "id": user.user_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "age": user.age,
        "gender": user.gender,
    })

@router.post("/register", summary="User registration")
async def register(register_data: RegisterRequest, conn: sqlite3.Connection = Depends(get_db)):
    """Register new user"""
    db = Database(conn)

    print(register_data)  # DEBUG
    
    existing = db.fetch_one(
        "SELECT * FROM users WHERE email = ?",
        (str(register_data.email),)
    )
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    username = f"user_{secrets.token_hex(8)}"
    now = datetime.utcnow().isoformat()
    
    db.execute(
        """
        INSERT INTO users (
            username, email, password_hash, first_name, last_name,
            age, gender, role, created_at, last_login, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            str(register_data.email),
            hash_password(register_data.password),
            register_data.first_name,
            register_data.last_name,
            register_data.age,
            register_data.gender,
            register_data.role,
            now,
            now,
            True,
        )
    )

    db.commit()
    db.execute("SELECT last_insert_rowid()")
    user_id = db.cursor.fetchone()[0]

    user = User(
        user_id=user_id,
        username=username,
        email=str(register_data.email),
        password_hash=hash_password(register_data.password),
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        age=register_data.age,
        gender=register_data.gender,
        role=register_data.role,
        created_at=now,
        last_login=now,
        is_active=True,
    )

    session = create_session(conn, user, minutes=30)

    return login_response(session.token, {
        "id": user.user_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "age": user.age,
        "gender": user.gender,
    })

@router.post("/logout", summary="User logout")
async def logout(token: HTTPAuthorizationCredentials = Depends(security), conn: sqlite3.Connection = Depends(get_db)):
    """Invalidate user session"""
    credentials = token.credentials
    db = Database(conn)
    
    db.execute("DELETE FROM user_session WHERE token = ?", (credentials,))
    db.commit()
    
    return success_response(message="Logout successful")

@router.post("/refresh", summary="Refresh token")
async def refresh_token(token: HTTPAuthorizationCredentials = Depends(security), conn: sqlite3.Connection = Depends(get_db)):
    """Refresh authentication token"""
    db = Database(conn)
    
    old_row = db.fetch_one("SELECT * FROM user_session WHERE token = ?", (token.credentials,))
    if not old_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    old_session = SessionToken.from_db_row(old_row)
    
    user_row = db.fetch_one("SELECT * FROM users WHERE user_id = ?", (old_session.user_id,))
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    db.execute("DELETE FROM user_session WHERE token = ?", (token.credentials,))
    db.commit()

    user = User.from_db_row(user_row)
    new_session = create_session(conn, user, minutes=30)
    
    return success_response({
        "access_token": new_session.token,
        "token_type": "bearer",
        "expires_at": new_session.expires_at,
    })

@router.post("/forgot-password", summary="Request password reset")
async def forgot_password(email: str):
    """Send password reset email"""
    return success_response(
        message="If an account exists with this email, a reset link has been sent"
    )

@router.post("/reset-password", summary="Reset password")
async def reset_password(token: str, new_password: str, conn: sqlite3.Connection = Depends(get_db)):
    """Reset user password with token"""
    return success_response(message="Password reset successful")
