import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.auth_db import (
    hash_password,
    verify_password,
    create_session,
    get_current_user,
    get_current_admin
)
from api.db_models import User, SessionToken


class TestHashPassword:
    """Tests for password hashing function"""
    
    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing creates a valid hash"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert "pbkdf2" in hashed
        assert "$" in hashed

    def test_hash_password_different_salts(self):
        """Test that same password with different salts produces different hashes"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2

    def test_hash_password_consistent_with_salt(self):
        """Test that password hash is consistent when salt is provided"""
        password = "test_password_123"
        hash1 = hash_password(password)
        
        # Extract salt from hash
        parts = hash1.split("$")
        salt = parts[2]
        
        # Hash again with same salt
        hash2 = hash_password(password, salt=salt)
        
        assert hash1 == hash2


class TestVerifyPassword:
    """Tests for password verification function"""
    
    def test_verify_correct_password(self):
        """Test that correct password is verified successfully"""
        password = "correct_password"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True

    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_empty_password(self):
        """Test verification with empty password"""
        password = "test"
        hashed = hash_password(password)
        
        result = verify_password("", hashed)
        
        assert result is False

    def test_verify_invalid_hash_format(self):
        """Test verification with invalid hash format"""
        result = verify_password("password", "invalid_hash")
        
        assert result is False

    def test_verify_non_pbkdf2_hash(self):
        """Test verification with non-pbkdf2 hash"""
        invalid_hash = "other$120000$salt$hash"
        
        result = verify_password("password", invalid_hash)
        
        assert result is False


class TestCreateSession:
    """Tests for session creation function"""
    
    def test_create_session_success(self):
        """Test successful session creation"""
        db = MagicMock()
        user = MagicMock()
        user.id = "user123"
        
        session = create_session(db, user, minutes=30)
        
        assert session.user_id == "user123"
        assert session.token is not None
        assert "tok_" in session.token
        assert db.add.called
        assert db.commit.called
        assert db.refresh.called

    def test_create_session_custom_expiry(self):
        """Test session creation with custom expiry time"""
        db = MagicMock()
        user = MagicMock()
        user.id = "user456"
        
        before = datetime.utcnow()
        session = create_session(db, user, minutes=60)
        after = datetime.utcnow()
        
        # Check expiry is approximately 60 minutes from now
        expected_min = before + timedelta(minutes=59)
        expected_max = after + timedelta(minutes=61)
        
        assert expected_min <= session.expires_at <= expected_max

    def test_create_session_token_format(self):
        """Test that session token has correct format"""
        db = MagicMock()
        user = MagicMock()
        user.id = "user789"
        
        session = create_session(db, user)
        
        assert session.token.startswith("tok_")
        assert len(session.token) > 4


class TestGetCurrentUser:
    """Tests for get_current_user dependency"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test retrieving user with valid token"""
        db = MagicMock()
        credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="tok_validtoken123")
        
        # Mock session token
        session = MagicMock()
        session.expires_at = datetime.utcnow() + timedelta(minutes=30)
        session.user_id = "user123"
        
        # Mock user
        user = MagicMock()
        user.id = "user123"
        user.is_active = True
        user.to_public_dict.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "account_type": "user"
        }
        
        db.get.side_effect = lambda model, id: session if model == SessionToken else user
        
        result = await get_current_user(credentials=credentials, db=db)
        
        assert result["id"] == "user123"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test error with invalid token"""
        db = MagicMock()
        credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="tok_invalidtoken")
        
        db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        """Test error with expired token"""
        db = MagicMock()
        credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="tok_expiredtoken")
        
        # Mock expired session
        session = MagicMock()
        session.expires_at = datetime.utcnow() - timedelta(minutes=30)
        session.user_id = "user123"
        
        db.get.return_value = session
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db)
        
        assert exc_info.value.status_code == 401
        assert db.delete.called

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self):
        """Test error when user is inactive"""
        db = MagicMock()
        credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="tok_validtoken")
        
        session = MagicMock()
        session.expires_at = datetime.utcnow() + timedelta(minutes=30)
        session.user_id = "user123"
        
        user = MagicMock()
        user.is_active = False
        
        db.get.side_effect = lambda model, id: session if model == SessionToken else user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test error when user doesn't exist"""
        db = MagicMock()
        credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="tok_validtoken")
        
        session = MagicMock()
        session.expires_at = datetime.utcnow() + timedelta(minutes=30)
        session.user_id = "nonexistent_user"
        
        db.get.side_effect = lambda model, id: session if model == SessionToken else None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentAdmin:
    """Tests for get_current_admin dependency"""
    
    @pytest.mark.asyncio
    async def test_get_current_admin_valid_admin(self):
        """Test admin access with valid admin user"""
        user = {"id": "admin123", "account_type": "admin"}
        
        result = await get_current_admin(user=user)
        
        assert result["id"] == "admin123"
        assert result["account_type"] == "admin"

    @pytest.mark.asyncio
    async def test_get_current_admin_non_admin_user(self):
        """Test error when user is not admin"""
        user = {"id": "user123", "account_type": "user"}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(user=user)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_admin_missing_account_type(self):
        """Test error when account_type is missing"""
        user = {"id": "user123"}
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(user=user)
        
        assert exc_info.value.status_code == 403
