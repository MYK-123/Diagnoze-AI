import pytest
import sqlite3
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from api.main import app
from api.database import Database, get_db
from api.db_models import User, SessionToken, ChatSession, ChatMessage, ChatHistory
from api.auth_db import hash_password, verify_password, create_session, get_current_user, get_current_admin

@pytest.fixture(scope="function")
def test_db_connection():
    """Create an in-memory test database"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age INTEGER NOT NULL DEFAULT 18,
        gender TEXT NOT NULL DEFAULT 'prefer_not_to_say',
        account_type TEXT NOT NULL DEFAULT 'user',
        phone TEXT,
        preferences_json TEXT NOT NULL DEFAULT '{}',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN NOT NULL DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE chat_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        state TEXT NOT NULL DEFAULT 'welcome',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data_json TEXT,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE chat_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        duration TEXT NOT NULL DEFAULT 'N/A',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        predictions_json TEXT NOT NULL DEFAULT '[]',
        messages_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def override_get_db(test_db_connection):
    """Override get_db dependency"""
    def _get_db():
        yield test_db_connection
    
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db):
    """Create test client"""
    return TestClient(app)

class TestAuthDBFunctions:
    """Tests for auth_db functions"""
    
    def test_hash_and_verify_password_cycle(self):
        """Test password hashing and verification cycle"""
        password = "TestPassword123!@#"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)
    
    def test_create_session_with_default_expiry(self, test_db_connection):
        """Test creating session with default 30-minute expiry"""
        user = User(
            id="test_user",
            email="test@example.com",
            password_hash=hash_password("pass"),
            first_name="Test",
            last_name="User"
        )
        
        session = create_session(test_db_connection, user)
        assert session.token.startswith("tok_")
        assert session.user_id == "test_user"
    
    def test_create_session_with_custom_expiry(self, test_db_connection):
        """Test creating session with custom expiry"""
        user = User(
            id="test_user",
            email="test@example.com",
            password_hash=hash_password("pass"),
            first_name="Test",
            last_name="User"
        )
        
        before = datetime.utcnow()
        session = create_session(test_db_connection, user, minutes=120)
        after = datetime.utcnow()
        
        expires = datetime.fromisoformat(session.expires_at)
        assert before + timedelta(minutes=119) <= expires <= after + timedelta(minutes=121)

@pytest.mark.asyncio
class TestAuthDBAsync:
    """Tests for async auth_db functions"""
    
    async def test_get_current_user_with_valid_session(self, test_db_connection):
        """Test getting current user with valid session"""
        from fastapi.security import HTTPAuthorizationCredentials
        
        db = Database(test_db_connection)
        
        # Create test user
        user = User(
            id="user_123",
            email="test@example.com",
            password_hash=hash_password("password"),
            first_name="John",
            last_name="Doe",
            is_active=True
        )
        
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user.id, user.email, user.password_hash, user.first_name, user.last_name, 1)
        )
        db.commit()
        
        # Create session
        session = create_session(test_db_connection, user)
        
        # Get current user
        creds = HTTPAuthorizationCredentials(scheme="bearer", credentials=session.token)
        current_user = await get_current_user(credentials=creds, conn=test_db_connection)
        
        assert current_user["id"] == "user_123"
        assert current_user["email"] == "test@example.com"
    
    async def test_get_current_user_with_invalid_session(self, test_db_connection):
        """Test error when session is invalid"""
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        creds = HTTPAuthorizationCredentials(scheme="bearer", credentials="invalid_token_xyz")
        
        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=creds, conn=test_db_connection)
        
        assert exc.value.status_code == 401
    
    async def test_get_current_admin_with_admin_user(self):
        """Test get_current_admin with admin account"""
        admin_user = {"id": "admin_1", "account_type": "admin"}
        result = await get_current_admin(user=admin_user)
        assert result["account_type"] == "admin"
    
    async def test_get_current_admin_with_regular_user(self):
        """Test error when regular user tries to access admin"""
        from fastapi import HTTPException
        
        regular_user = {"id": "user_1", "account_type": "user"}
        
        with pytest.raises(HTTPException) as exc:
            await get_current_admin(user=regular_user)
        
        assert exc.value.status_code == 403

class TestAuthRouter:
    """Tests for authentication router"""
    
    def test_register_new_user(self, client):
        """Test registering a new user"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "first_name": "Alice",
                "last_name": "Smith",
                "age": 28,
                "gender": "female"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data.get("data", {})
    
    def test_register_duplicate_email(self, client, test_db_connection):
        """Test registering with duplicate email"""
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "taken@example.com", hash_password("pass"), "John", "Doe")
        )
        db.commit()
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "taken@example.com",
                "password": "NewPass123!",
                "first_name": "Jane",
                "last_name": "Smith",
                "age": 25
            }
        )
        
        assert response.status_code == 400
    
    def test_login_user(self, client, test_db_connection):
        """Test logging in a user"""
        db = Database(test_db_connection)
        password = "UserPass123!"
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("user1", "login@example.com", hash_password(password), "Bob", "Johnson", 1)
        )
        db.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": password
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data.get("data", {})
    
    def test_login_invalid_credentials(self, client, test_db_connection):
        """Test login with wrong password"""
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", hash_password("correct"), "John", "Doe")
        )
        db.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
    
    def test_logout_user(self, client):
        """Test logging out a user"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer tok_test_token"}
        )
        
        assert response.status_code == 200
    
    def test_refresh_token_invalid(self, client):
        """Test refreshing with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_forgot_password_endpoint(self, client):
        """Test forgot password endpoint"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "user@example.com"}
        )
        
        assert response.status_code == 200
    
    def test_reset_password_endpoint(self, client):
        """Test reset password endpoint"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "reset_token_123", "new_password": "NewPass456!"}
        )
        
        assert response.status_code == 200

class TestUsersRouter:
    """Tests for users router"""
    
    @patch('api.routers.users.get_current_user')
    def test_get_user_profile(self, mock_user, client):
        """Test getting user profile"""
        mock_user.return_value = {
            "id": "user1",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "account_type": "user"
        }
        
        response = client.get(
            "/api/v1/users/profile",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "user1"
    
    @patch('api.routers.users.get_current_user')
    def test_update_user_profile(self, mock_user, client, test_db_connection):
        """Test updating user profile"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        response = client.put(
            "/api/v1/users/profile",
            json={"first_name": "Jane", "age": 30},
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.users.get_current_user')
    def test_get_chat_history(self, mock_user, client, test_db_connection):
        """Test getting user chat history"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.get(
            "/api/v1/users/history",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "chats" in data.get("data", {})
    
    @patch('api.routers.users.get_current_user')
    def test_get_user_stats(self, mock_user, client, test_db_connection):
        """Test getting user statistics"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.get(
            "/api/v1/users/stats",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_chats" in data.get("data", {})

class TestAdminRouter:
    """Tests for admin router"""
    
    @patch('api.routers.admin.get_current_admin')
    def test_get_all_users(self, mock_admin, client, test_db_connection):
        """Test getting all users (admin only)"""
        mock_admin.return_value = {"id": "admin1", "account_type": "admin"}
        
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.admin.get_current_admin')
    def test_get_analytics(self, mock_admin, client, test_db_connection):
        """Test getting system analytics (admin only)"""
        mock_admin.return_value = {"id": "admin1", "account_type": "admin"}
        
        response = client.get(
            "/api/v1/admin/analytics",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data.get("data", {})
    
    @patch('api.routers.admin.get_current_admin')
    def test_update_user_role(self, mock_admin, client, test_db_connection):
        """Test updating user role (admin only)"""
        mock_admin.return_value = {"id": "admin1", "account_type": "admin"}
        
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name, account_type)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", "hash", "John", "Doe", "user")
        )
        db.commit()
        
        response = client.put(
            "/api/v1/admin/users/user1",
            json={"account_type": "medical_student"},
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.admin.get_current_admin')
    def test_delete_user(self, mock_admin, client, test_db_connection):
        """Test deleting a user (admin only)"""
        mock_admin.return_value = {"id": "admin1", "account_type": "admin"}
        
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        response = client.delete(
            "/api/v1/admin/users/user1",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.admin.get_current_admin')
    def test_cannot_delete_self(self, mock_admin, client, test_db_connection):
        """Test admin cannot delete their own account"""
        mock_admin.return_value = {"id": "admin1", "account_type": "admin"}
        
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("admin1", "admin@example.com", "hash", "Admin", "User")
        )
        db.commit()
        
        response = client.delete(
            "/api/v1/admin/users/admin1",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 400

class TestEndpointValidation:
    """Tests for endpoint validation and error handling"""
    
    def test_missing_auth_header(self, client):
        """Test accessing protected endpoint without auth"""
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 403
    
    def test_invalid_email_format(self, client):
        """Test validation of email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "Pass123!",
                "first_name": "John",
                "last_name": "Doe",
                "age": 25
            }
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling missing required fields"""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 422
