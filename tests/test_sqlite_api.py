import pytest
import sqlite3
import json
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from api.main import app
from api.database import Database, get_connection, init_db, get_db
from api.db_models import (
    User, SessionToken, ChatSession, ChatMessage, ChatHistory,
    _json_dumps, _json_loads, _now
)
from api.auth_db import (
    hash_password, verify_password, create_session, get_current_user, get_current_admin
)

# Test Database Setup
@pytest.fixture(scope="function")
def test_db_connection():
    """Create an in-memory test database"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Initialize schema
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

# ==================== Database Tests ====================
class TestDatabase:
    """Tests for Database wrapper class"""
    
    def test_database_execute(self, test_db_connection):
        """Test execute method"""
        db = Database(test_db_connection)
        cursor = db.execute("SELECT 1 as test")
        result = cursor.fetchone()
        assert result[0] == 1
    
    def test_database_fetch_one(self, test_db_connection):
        """Test fetch_one method"""
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        result = db.fetch_one("SELECT * FROM users WHERE id = ?", ("user1",))
        assert result is not None
        assert result["email"] == "test@example.com"
    
    def test_database_fetch_all(self, test_db_connection):
        """Test fetch_all method"""
        db = Database(test_db_connection)
        for i in range(3):
            db.execute(
                "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"user{i}", f"test{i}@example.com", "hash", "John", "Doe")
            )
        db.commit()
        
        results = db.fetch_all("SELECT * FROM users")
        assert len(results) == 3
    
    def test_database_fetch_scalar(self, test_db_connection):
        """Test fetch_scalar method"""
        db = Database(test_db_connection)
        for i in range(5):
            db.execute(
                "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"user{i}", f"test{i}@example.com", "hash", "John", "Doe")
            )
        db.commit()
        
        count = db.fetch_scalar("SELECT COUNT(*) FROM users")
        assert count == 5
    
    def test_database_commit(self, test_db_connection):
        """Test commit method"""
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        # Verify data persisted
        result = db.fetch_one("SELECT * FROM users WHERE id = ?", ("user1",))
        assert result is not None

# ==================== Model Tests ====================
class TestUserModel:
    """Tests for User model"""
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash_value",
            first_name="John",
            last_name="Doe",
        )
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.is_active is True
    
    def test_user_to_public_dict(self):
        """Test user to_public_dict"""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash_value",
            first_name="John",
            last_name="Doe",
            phone="1234567890"
        )
        public = user.to_public_dict()
        assert "id" in public
        assert "email" in public
        assert "password_hash" not in public
        assert public["phone"] == "1234567890"
    
    def test_user_from_db_row(self):
        """Test creating user from database row"""
        row = {
            "id": "user1",
            "email": "test@example.com",
            "password_hash": "hash",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "gender": "male",
            "account_type": "user",
            "phone": None,
            "preferences_json": "{}",
            "created_at": "2023-01-01T00:00:00",
            "last_login": None,
            "is_active": 1,
        }
        user = User.from_db_row(row)
        assert user.id == "user1"
        assert user.email == "test@example.com"
        assert user.age == 30

class TestSessionTokenModel:
    """Tests for SessionToken model"""
    
    def test_session_token_creation(self):
        """Test creating session token"""
        token = SessionToken(
            token="tok_test123",
            user_id="user123",
            expires_at="2025-12-31T00:00:00"
        )
        assert token.token == "tok_test123"
        assert token.user_id == "user123"
    
    def test_session_token_new_token(self):
        """Test generating new token"""
        token = SessionToken.new_token()
        assert token.startswith("tok_")
        assert len(token) > 10
    
    def test_session_token_from_db_row(self):
        """Test creating session token from db row"""
        row = {
            "token": "tok_test",
            "user_id": "user1",
            "created_at": "2023-01-01T00:00:00",
            "expires_at": "2023-01-02T00:00:00"
        }
        session = SessionToken.from_db_row(row)
        assert session.token == "tok_test"
        assert session.user_id == "user1"

class TestChatSessionModel:
    """Tests for ChatSession model"""
    
    def test_chat_session_creation(self):
        """Test creating chat session"""
        session = ChatSession(
            id="session_123",
            user_id="user123",
            state="welcome"
        )
        assert session.id == "session_123"
        assert session.state == "welcome"
        assert session.symptoms() == []
    
    def test_chat_session_symptoms(self):
        """Test symptoms management"""
        session = ChatSession(
            id="session_123",
            user_id="user123"
        )
        session.set_symptoms(["headache", "fever", "cough"])
        
        symptoms = session.symptoms()
        assert "headache" in symptoms
        assert len(symptoms) == 3
    
    def test_chat_session_symptoms_dedup(self):
        """Test symptoms deduplication"""
        session = ChatSession(id="s1", user_id="u1")
        session.set_symptoms(["headache", "headache", "fever"])
        
        symptoms = session.symptoms()
        assert symptoms.count("headache") == 1

class TestChatMessageModel:
    """Tests for ChatMessage model"""
    
    def test_chat_message_creation(self):
        """Test creating chat message"""
        msg = ChatMessage(
            session_id="session_123",
            role="user",
            content="Hello"
        )
        assert msg.session_id == "session_123"
        assert msg.role == "user"
    
    def test_chat_message_to_dict(self):
        """Test message to_dict"""
        msg = ChatMessage(
            session_id="s1",
            role="assistant",
            content="Response",
            timestamp="2023-01-01T00:00:00"
        )
        msg_dict = msg.to_dict()
        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Response"
        assert "timestamp" in msg_dict

class TestChatHistoryModel:
    """Tests for ChatHistory model"""
    
    def test_chat_history_creation(self):
        """Test creating chat history"""
        history = ChatHistory(
            id="chat_123",
            user_id="user123",
            title="My Chat"
        )
        assert history.id == "chat_123"
        assert history.title == "My Chat"
    
    def test_chat_history_to_dict(self):
        """Test history to_dict"""
        history = ChatHistory(
            id="chat_123",
            user_id="user123",
            title="Test",
            created_at="2023-01-01T12:00:00",
            ended_at="2023-01-01T12:30:00",
            symptoms_json=_json_dumps(["fever", "cough"])
        )
        history_dict = history.to_dict()
        assert history_dict["title"] == "Test"
        assert len(history_dict["symptoms"]) == 2

# ==================== Auth Tests ====================
class TestPasswordHashing:
    """Tests for password hashing"""
    
    def test_hash_password_format(self):
        """Test hash format"""
        hash_val = hash_password("password123")
        assert "pbkdf2" in hash_val
        assert "$" in hash_val
    
    def test_hash_password_different_salts(self):
        """Test different salts produce different hashes"""
        hash1 = hash_password("password")
        hash2 = hash_password("password")
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False
    
    def test_verify_invalid_hash(self):
        """Test verifying invalid hash"""
        assert verify_password("password", "invalid_hash") is False

class TestCreateSession:
    """Tests for create_session"""
    
    def test_create_session(self, test_db_connection):
        """Test session creation"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hash",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(test_db_connection, user, minutes=30)
        
        assert session.token is not None
        assert session.user_id == "user1"
        assert session.token.startswith("tok_")
    
    def test_create_session_stored(self, test_db_connection):
        """Test session is stored in database"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hash",
            first_name="John",
            last_name="Doe"
        )
        
        session = create_session(test_db_connection, user)
        
        # Verify in database
        db = Database(test_db_connection)
        stored = db.fetch_one("SELECT * FROM sessions WHERE token = ?", (session.token,))
        assert stored is not None
        assert stored["user_id"] == "user1"

# ==================== API Tests ====================
class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root returns correct data"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Diagnoze AI API"
        assert data["version"] == "1.0.0"

class TestHealthEndpoint:
    """Tests for health endpoint"""
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "diagnoze-api"

class TestAuthRegister:
    """Tests for registration"""
    
    def test_register_success(self, client, test_db_connection):
        """Test successful registration"""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 25,
            "gender": "female",
            "account_type": "user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]
    
    def test_register_duplicate_email(self, client, test_db_connection):
        """Test registration with existing email"""
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "existing@example.com", hash_password("pass"), "John", "Doe")
        )
        db.commit()
        
        response = client.post("/api/v1/auth/register", json={
            "email": "existing@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 25
        })
        
        assert response.status_code == 400

class TestAuthLogin:
    """Tests for login"""
    
    def test_login_success(self, client, test_db_connection):
        """Test successful login"""
        db = Database(test_db_connection)
        password = "mypassword123"
        hashed = hash_password(password)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", hashed, "John", "Doe", 1)
        )
        db.commit()
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": password
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]
    
    def test_login_wrong_password(self, client, test_db_connection):
        """Test login with wrong password"""
        db = Database(test_db_connection)
        db.execute(
            """INSERT INTO users (id, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            ("user1", "test@example.com", hash_password("correct"), "John", "Doe")
        )
        db.commit()
        
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrong"
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post("/api/v1/auth/login", json={
            "email": "notfound@example.com",
            "password": "password"
        })
        
        assert response.status_code == 401

class TestJsonUtilities:
    """Tests for JSON utilities"""
    
    def test_json_dumps(self):
        """Test JSON dumps"""
        data = {"name": "test", "value": 123}
        result = _json_dumps(data)
        assert isinstance(result, str)
        assert "name" in result
    
    def test_json_loads(self):
        """Test JSON loads"""
        json_str = '{"name": "test"}'
        result = _json_loads(json_str)
        assert result["name"] == "test"
    
    def test_json_loads_none(self):
        """Test JSON loads with None"""
        assert _json_loads(None) is None
        assert _json_loads("") is None
    
    def test_json_round_trip(self):
        """Test round trip"""
        original = {"items": [1, 2, 3], "name": "test"}
        dumped = _json_dumps(original)
        loaded = _json_loads(dumped)
        assert loaded == original

class TestSystemStats:
    """Tests for system stats endpoint"""
    
    @patch('api.main.get_current_user')
    def test_system_stats(self, mock_user, client, test_db_connection):
        """Test system stats endpoint"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        response = client.get(
            "/api/v1/system/stats",
            headers={"Authorization": "Bearer tok_test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data["data"]
        assert "total_chats" in data["data"]
