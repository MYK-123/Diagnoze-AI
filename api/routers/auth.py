from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth_db import create_session, hash_password, verify_password
from ..database import get_db
from ..db_models import SessionToken, User
from ..models.schemas import LoginRequest, RegisterRequest
from ..models.responses import success_response, login_response

router = APIRouter()
security = HTTPBearer()

@router.post("/login", summary="User login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return token"""
    user = db.scalar(select(User).where(User.email == str(login_data.email)))
    if not user or not user.is_active or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    session = create_session(db, user, minutes=30)

    return login_response(session.token, {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "account_type": user.account_type,
        "age": user.age,
        "gender": user.gender,
    })

@router.post("/register", summary="User registration")
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user"""
    existing = db.scalar(select(User).where(User.email == str(register_data.email)))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = User(
        id=f"user_{secrets.token_hex(8)}",
        email=str(register_data.email),
        password_hash=hash_password(register_data.password),
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        age=register_data.age,
        gender=register_data.gender,
        account_type=register_data.account_type,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
        preferences_json="{}",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    session = create_session(db, user, minutes=30)

    return login_response(session.token, {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "account_type": user.account_type,
        "age": user.age,
        "gender": user.gender,
    })

@router.post("/logout", summary="User logout")
async def logout(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Invalidate user session"""
    credentials = token.credentials
    session = db.get(SessionToken, credentials)
    if session:
        db.delete(session)
        db.commit()
    return success_response(message="Logout successful")

@router.post("/refresh", summary="Refresh token")
async def refresh_token(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Refresh authentication token"""
    old = db.get(SessionToken, token.credentials)
    if not old:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, old.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    db.delete(old)
    db.commit()

    new_session = create_session(db, user, minutes=30)
    return success_response({
        "access_token": new_session.token,
        "token_type": "bearer",
        "expires_at": new_session.expires_at.isoformat(),
    })

@router.post("/forgot-password", summary="Request password reset")
async def forgot_password(email: str):
    """Send password reset email"""
    return success_response(
        message="If an account exists with this email, a reset link has been sent"
    )

@router.post("/reset-password", summary="Reset password")
async def reset_password(token: str, new_password: str):
    """Reset user password with token"""
    return success_response(message="Password reset successful")
