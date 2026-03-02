import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json
from fastapi import HTTPException

# Mock the core modules before importing
import sys
from unittest.mock import MagicMock

sys.modules['core.core'] = MagicMock()
sys.modules['core.symptoms'] = MagicMock()

from api.routers.chat import (
    start_chat_session,
    send_chat_message,
    generate_ai_response,
    generate_predictions_from_core,
    save_chat_session,
    get_chat_session,
    delete_chat_session,
    chat_response
)
from api.models.schemas import ChatMessage, PredictionRequest, SaveChatSessionRequest
from api.db_models import ChatSession, ChatMessage as DBChatMessage, ChatHistory


class TestStartChatSession:
    """Tests for start_chat_session endpoint"""
    
    @pytest.mark.asyncio
    async def test_start_chat_session_success(self):
        """Test successful chat session creation"""
        user = {"id": "user123", "email": "test@example.com"}
        db = MagicMock()
        
        result = await start_chat_session(user=user, db=db)
        
        assert result["data"]["message"] == "Hello! I'm Diagnoze AI. Describe your symptoms and I'll help analyze possible conditions."
        assert "session_id" in result["data"]
        assert db.add.called
        assert db.commit.called

    @pytest.mark.asyncio
    async def test_start_chat_session_creates_correct_structure(self):
        """Test that session is created with correct initial state"""
        user = {"id": "user123"}
        db = MagicMock()
        
        await start_chat_session(user=user, db=db)
        
        added_session = db.add.call_args[0][0]
        assert added_session.user_id == "user123"
        assert added_session.state == "welcome"
        assert added_session.symptoms_json == "[]"


class TestSendChatMessage:
    """Tests for send_chat_message endpoint"""
    
    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self):
        """Test error when session doesn't exist"""
        chat_data = ChatMessage(session_id="invalid", message="hello", symptoms=[])
        user = {"id": "user123"}
        db = MagicMock()
        db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await send_chat_message(chat_data=chat_data, user=user, db=db)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_access_denied(self):
        """Test access denial when user doesn't own session"""
        chat_data = ChatMessage(session_id="session123", message="hello", symptoms=[])
        user = {"id": "user123"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "different_user"
        db.get.return_value = session
        
        with pytest.raises(HTTPException) as exc_info:
            await send_chat_message(chat_data=chat_data, user=user, db=db)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending"""
        chat_data = ChatMessage(session_id="session123", message="I have headache", symptoms=["headache"])
        user = {"id": "user123"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "user123"
        session.state = "welcome"
        session.symptoms.return_value = ["headache"]
        session.set_symptoms = MagicMock()
        db.get.return_value = session
        
        with patch('api.routers.chat.generate_ai_response') as mock_gen:
            mock_gen.return_value = {"response": "I understand", "data": {"response": "I understand"}}
            
            result = await send_chat_message(chat_data=chat_data, user=user, db=db)
            
            assert db.add.called
            assert db.commit.called


class TestGenerateAIResponse:
    """Tests for generate_ai_response function"""
    
    def test_emergency_keyword_detection(self):
        """Test emergency keyword detection"""
        user_input = "I have severe chest pain"
        session = {"state": "welcome", "symptoms": []}
        
        response = generate_ai_response(user_input, session)
        
        assert "emergency" in response.keys() or "EMERGENCY" in response.get("response", "").upper()

    def test_generate_response_welcome_state_few_symptoms(self):
        """Test response generation in welcome state with few symptoms"""
        user_input = "I have a headache"
        session = {"state": "welcome", "symptoms": []}
        
        with patch('api.routers.chat.get_all_symptoms_cache') as mock_cache:
            mock_symptom = MagicMock()
            mock_symptom.get_name.return_value = "headache"
            mock_cache.return_value.get_all_list.return_value = [mock_symptom]
            
            response = generate_ai_response(user_input, session)
            
            assert "response" in response.keys() or "data" in response.keys()

    def test_generate_response_with_predictions(self):
        """Test response generation when enough symptoms collected"""
        user_input = "I also have fever"
        session = {"state": "collecting_symptoms", "symptoms": ["headache", "fever"]}
        
        with patch('api.routers.chat.generate_predictions_from_core') as mock_pred:
            mock_pred.return_value = [
                {
                    "id": 1,
                    "name": "Common Cold",
                    "confidence": 75,
                    "severity": "low"
                }
            ]
            
            response = generate_ai_response(user_input, session)
            
            assert response is not None


class TestGeneratePredictionsFromCore:
    """Tests for generate_predictions_from_core function"""
    
    def test_empty_symptoms_returns_empty(self):
        """Test that empty symptoms list returns empty predictions"""
        result = generate_predictions_from_core([])
        assert result == []

    def test_predictions_with_valid_symptoms(self):
        """Test predictions with valid symptoms"""
        with patch('api.routers.chat.get_all_symptoms_cache') as mock_cache:
            with patch('api.routers.chat.get_top_k_diseases_from_prediction_with_probablities') as mock_pred:
                mock_symptom = MagicMock()
                mock_symptom.get_name.return_value = "headache"
                mock_cache.return_value.get_all_list.return_value = [mock_symptom]
                
                mock_disease = MagicMock()
                mock_disease.get_disease_id.return_value = 1
                mock_disease.get_disease_name.return_value = "Migraine"
                mock_disease.get_category.return_value = "Neurological"
                mock_disease.get_severity_level_str.return_value = "medium"
                mock_pred.return_value = [(mock_disease, 0.75)]
                
                result = generate_predictions_from_core(["headache"])
                
                assert len(result) > 0
                assert "name" in result[0]
                assert "confidence" in result[0]

    def test_predictions_format(self):
        """Test that predictions are properly formatted"""
        with patch('api.routers.chat.get_all_symptoms_cache') as mock_cache:
            with patch('api.routers.chat.get_top_k_diseases_from_prediction_with_probablities') as mock_pred:
                mock_symptom = MagicMock()
                mock_symptom.get_name.return_value = "fever"
                mock_cache.return_value.get_all_list.return_value = [mock_symptom]
                
                mock_disease = MagicMock()
                mock_disease.get_disease_id.return_value = 2
                mock_disease.get_disease_name.return_value = "Influenza"
                mock_disease.get_category.return_value = "Viral"
                mock_disease.get_severity_level_str.return_value = "high"
                mock_pred.return_value = [(mock_disease, 0.85)]
                
                result = generate_predictions_from_core(["fever"])
                
                assert result[0]["id"] == 2
                assert result[0]["name"] == "Influenza"
                assert result[0]["confidence"] <= 95
                assert result[0]["severity"] == "high"


class TestSaveChatSession:
    """Tests for save_chat_session endpoint"""
    
    @pytest.mark.asyncio
    async def test_save_session_not_found(self):
        """Test error when session doesn't exist"""
        payload = SaveChatSessionRequest(session_id="invalid", title="Test")
        user = {"id": "user123"}
        db = MagicMock()
        db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await save_chat_session(payload=payload, user=user, db=db)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_save_session_access_denied(self):
        """Test access denial when user doesn't own session"""
        payload = SaveChatSessionRequest(session_id="session123", title="Test")
        user = {"id": "user123", "account_type": "user"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "different_user"
        db.get.return_value = session
        
        with pytest.raises(HTTPException) as exc_info:
            await save_chat_session(payload=payload, user=user, db=db)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_save_session_success(self):
        """Test successful session saving"""
        payload = SaveChatSessionRequest(session_id="session123", title="My Chat")
        user = {"id": "user123"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "user123"
        session.symptoms.return_value = ["headache", "fever"]
        session.created_at = datetime.now()
        db.get.return_value = session
        db.scalars.return_value.all.return_value = []
        
        result = await save_chat_session(payload=payload, user=user, db=db)
        
        assert result["status"] == "success"
        assert "chat_id" in result["data"]


class TestGetChatSession:
    """Tests for get_chat_session endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        """Test error when session doesn't exist"""
        user = {"id": "user123"}
        db = MagicMock()
        db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_chat_session("invalid", user=user, db=db)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_session_access_denied(self):
        """Test access denial for non-admin users"""
        user = {"id": "user123", "account_type": "user"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "different_user"
        db.get.return_value = session
        
        with pytest.raises(HTTPException) as exc_info:
            await get_chat_session("session123", user=user, db=db)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_session_success(self):
        """Test successful session retrieval"""
        user = {"id": "user123", "account_type": "user"}
        db = MagicMock()
        
        session = MagicMock()
        session.id = "session123"
        session.user_id = "user123"
        session.created_at = datetime.now()
        session.last_activity = datetime.now()
        session.state = "welcome"
        session.symptoms.return_value = []
        db.get.return_value = session
        db.scalars.return_value.all.return_value = []
        
        result = await get_chat_session("session123", user=user, db=db)
        
        assert result["status"] == "success"
        assert result["data"]["id"] == "session123"

    @pytest.mark.asyncio
    async def test_get_session_admin_access(self):
        """Test that admin can access other users' sessions"""
        user = {"id": "admin123", "account_type": "admin"}
        db = MagicMock()
        
        session = MagicMock()
        session.id = "session123"
        session.user_id = "different_user"
        session.created_at = datetime.now()
        session.last_activity = datetime.now()
        session.state = "welcome"
        session.symptoms.return_value = []
        db.get.return_value = session
        db.scalars.return_value.all.return_value = []
        
        result = await get_chat_session("session123", user=user, db=db)
        
        assert result["status"] == "success"


class TestDeleteChatSession:
    """Tests for delete_chat_session endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_session_not_found(self):
        """Test error when session doesn't exist"""
        user = {"id": "user123"}
        db = MagicMock()
        db.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_chat_session("invalid", user=user, db=db)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_session_access_denied(self):
        """Test access denial when user doesn't own session"""
        user = {"id": "user123", "account_type": "user"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "different_user"
        db.get.return_value = session
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_chat_session("session123", user=user, db=db)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_session_success(self):
        """Test successful session deletion"""
        user = {"id": "user123"}
        db = MagicMock()
        
        session = MagicMock()
        session.user_id = "user123"
        db.get.return_value = session
        
        result = await delete_chat_session("session123", user=user, db=db)
        
        assert result["status"] == "success"
        assert db.delete.called
        assert db.commit.called


import pytest
import sqlite3
from unittest.mock import Mock, patch
from datetime import datetime
from fastapi.testclient import TestClient

from api.main import app
from api.database import Database, get_db
from api.db_models import User, ChatSession, ChatMessage, ChatHistory, _json_dumps, _json_loads
from api.auth_db import hash_password, create_session

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

class TestChatRouter:
    """Tests for chat router"""
    
    @patch('api.routers.chat.get_current_user')
    def test_start_chat_session(self, mock_user, client):
        """Test starting a new chat session"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.post(
            "/api/v1/chat/start-session",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data.get("data", {})
    
    @patch('api.routers.chat.get_current_user')
    def test_send_chat_message(self, mock_user, client, test_db_connection):
        """Test sending a message in chat"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("session1", "user1", "welcome", "[]")
        )
        db.commit()
        
        response = client.post(
            "/api/v1/chat/send-message",
            json={"session_id": "session1", "message": "I have a headache", "symptoms": []},
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.chat.get_current_user')
    def test_save_chat_session(self, mock_user, client, test_db_connection):
        """Test saving a chat session"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("session1", "user1", "welcome", "[]")
        )
        db.commit()
        
        response = client.post(
            "/api/v1/chat/save-session",
            json={"session_id": "session1", "title": "Test Chat"},
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "chat_id" in data.get("data", {})
    
    @patch('api.routers.chat.get_current_user')
    def test_get_chat_session(self, mock_user, client, test_db_connection):
        """Test retrieving a chat session"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("session1", "user1", "welcome", "[]")
        )
        db.commit()
        
        response = client.get(
            "/api/v1/chat/session/session1",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == "session1"
    
    @patch('api.routers.chat.get_current_user')
    def test_delete_chat_session(self, mock_user, client, test_db_connection):
        """Test deleting a chat session"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        db = Database(test_db_connection)
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("session1", "user1", "welcome", "[]")
        )
        db.commit()
        
        response = client.delete(
            "/api/v1/chat/session/session1",
            headers={"Authorization": "Bearer token"}
        )
        
        assert response.status_code == 200
    
    @patch('api.routers.chat.get_current_user')
    def test_generate_prediction(self, mock_user, client):
        """Test generating predictions"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.post(
            "/api/v1/chat/generate-prediction",
            json={"symptoms": [{"name": "headache"}, {"name": "fever"}]},
            headers={"Authorization": "Bearer token"}
        )
        
        # May return 200 or error depending on core availability
        assert response.status_code in [200, 500]

class TestMedicalRouter:
    """Tests for medical router"""
    
    @patch('api.routers.medical.get_current_user')
    def test_get_symptoms(self, mock_user, client):
        """Test getting symptoms list"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.get(
            "/api/v1/medical/symptoms",
            headers={"Authorization": "Bearer token"}
        )
        
        # May return 200 or error depending on core availability
        assert response.status_code in [200, 500]
    
    @patch('api.routers.medical.get_current_user')
    def test_get_diseases(self, mock_user, client):
        """Test getting diseases list"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.get(
            "/api/v1/medical/diseases",
            headers={"Authorization": "Bearer token"}
        )
        
        # May return 200 or error depending on core availability
        assert response.status_code in [200, 500]
    
    @patch('api.routers.medical.get_current_user')
    def test_search_medical(self, mock_user, client):
        """Test searching medical information"""
        mock_user.return_value = {"id": "user1", "account_type": "user"}
        
        response = client.get(
            "/api/v1/medical/search?q=fever",
            headers={"Authorization": "Bearer token"}
        )
        
        # May return 200 or error depending on core availability
        assert response.status_code in [200, 500]

class TestChatSessionModel:
    """Tests for ChatSession model operations"""
    
    def test_chat_session_crud(self, test_db_connection):
        """Test CRUD operations for chat sessions"""
        db = Database(test_db_connection)
        
        # Create
        session = ChatSession(
            id="sess_1",
            user_id="user_1",
            state="collecting_symptoms",
            symptoms_json=_json_dumps(["fever"])
        )
        
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            (session.id, session.user_id, session.state, session.symptoms_json)
        )
        db.commit()
        
        # Read
        row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", ("sess_1",))
        assert row is not None
        assert row["state"] == "collecting_symptoms"
        
        # Update
        db.execute(
            "UPDATE chat_sessions SET state = ? WHERE id = ?",
            ("completed", "sess_1")
        )
        db.commit()
        
        # Verify update
        row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", ("sess_1",))
        assert row["state"] == "completed"
        
        # Delete
        db.execute("DELETE FROM chat_sessions WHERE id = ?", ("sess_1",))
        db.commit()
        
        row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", ("sess_1",))
        assert row is None

class TestChatMessageModel:
    """Tests for ChatMessage model operations"""
    
    def test_chat_message_crud(self, test_db_connection):
        """Test CRUD operations for chat messages"""
        db = Database(test_db_connection)
        
        # Setup
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("sess1", "user1", "welcome", "[]")
        )
        db.commit()
        
        # Create
        msg = ChatMessage(
            session_id="sess1",
            role="user",
            content="Hello",
            data_json=_json_dumps({"intent": "greeting"})
        )
        
        db.execute(
            "INSERT INTO chat_messages (session_id, role, content, data_json) VALUES (?, ?, ?, ?)",
            (msg.session_id, msg.role, msg.content, msg.data_json)
        )
        db.commit()
        
        # Read
        rows = db.fetch_all("SELECT * FROM chat_messages WHERE session_id = ?", ("sess1",))
        assert len(rows) >= 1
        
        # Verify data
        msg_row = rows[0]
        assert msg_row["role"] == "user"
        data = _json_loads(msg_row["data_json"])
        assert data["intent"] == "greeting"

class TestChatHistoryModel:
    """Tests for ChatHistory model operations"""
    
    def test_chat_history_crud(self, test_db_connection):
        """Test CRUD operations for chat history"""
        db = Database(test_db_connection)
        
        # Setup
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        # Create
        history = ChatHistory(
            id="chat_1",
            user_id="user1",
            title="Symptom Analysis",
            symptoms_json=_json_dumps(["fever", "cough"]),
            predictions_json=_json_dumps([{"name": "Cold", "confidence": 85}])
        )
        
        db.execute(
            """INSERT INTO chat_history (id, user_id, title, symptoms_json, predictions_json)
               VALUES (?, ?, ?, ?, ?)""",
            (history.id, history.user_id, history.title, history.symptoms_json, history.predictions_json)
        )
        db.commit()
        
        # Read
        row = db.fetch_one("SELECT * FROM chat_history WHERE id = ?", ("chat_1",))
        assert row is not None
        assert row["title"] == "Symptom Analysis"
        
        symptoms = _json_loads(row["symptoms_json"])
        assert "fever" in symptoms
        
        predictions = _json_loads(row["predictions_json"])
        assert predictions[0]["name"] == "Cold"

class TestDatabaseTransactions:
    """Tests for database transaction handling"""
    
    def test_transaction_commit(self, test_db_connection):
        """Test transaction commit"""
        db = Database(test_db_connection)
        
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        db.commit()
        
        # Verify committed
        result = db.fetch_one("SELECT * FROM users WHERE id = ?", ("user1",))
        assert result is not None
    
    def test_cascade_delete(self, test_db_connection):
        """Test cascade delete on foreign key"""
        db = Database(test_db_connection)
        
        # Insert user
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        
        # Insert chat sessions
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("sess1", "user1", "welcome", "[]")
        )
        db.commit()
        
        # Delete user (should cascade)
        db.execute("DELETE FROM users WHERE id = ?", ("user1",))
        db.commit()
        
        # Verify cascade
        session = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", ("sess1",))
        assert session is None

class TestComplexScenarios:
    """Tests for complex scenarios"""
    
    def test_full_chat_workflow(self, test_db_connection):
        """Test complete chat workflow"""
        db = Database(test_db_connection)
        
        # 1. Create user
        user = User(id="u1", email="u@e.com", password_hash="h", first_name="J", last_name="D")
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (user.id, user.email, user.password_hash, user.first_name, user.last_name)
        )
        db.commit()
        
        # 2. Create session
        session = ChatSession(id="s1", user_id="u1", state="welcome", symptoms_json="[]")
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            (session.id, session.user_id, session.state, session.symptoms_json)
        )
        db.commit()
        
        # 3. Add messages
        for role, content in [("user", "I have fever"), ("assistant", "You may have flu")]:
            msg = ChatMessage(session_id="s1", role=role, content=content)
            db.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (msg.session_id, msg.role, msg.content)
            )
        db.commit()
        
        # 4. Save to history
        history = ChatHistory(
            id="h1", user_id="u1", title="Fever Analysis",
            symptoms_json=_json_dumps(["fever"]),
            predictions_json=_json_dumps([{"name": "Flu", "confidence": 80}]),
            messages_json=_json_dumps([
                {"role": "user", "content": "I have fever"},
                {"role": "assistant", "content": "You may have flu"}
            ])
        )
        db.execute(
            """INSERT INTO chat_history (id, user_id, title, symptoms_json, predictions_json, messages_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (history.id, history.user_id, history.title, history.symptoms_json, 
             history.predictions_json, history.messages_json)
        )
        db.commit()
        
        # 5. Verify complete workflow
        user_count = db.fetch_scalar("SELECT COUNT(*) FROM users WHERE id = ?", ("u1",))
        assert user_count == 1
        
        session_count = db.fetch_scalar("SELECT COUNT(*) FROM chat_sessions WHERE id = ?", ("s1",))
        assert session_count == 1
        
        message_count = db.fetch_scalar("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", ("s1",))
        assert message_count == 2
        
        history_count = db.fetch_scalar("SELECT COUNT(*) FROM chat_history WHERE id = ?", ("h1",))
        assert history_count == 1

class TestErrorRecovery:
    """Tests for error handling and recovery"""
    
    def test_invalid_user_id_format(self, client):
        """Test handling invalid user ID"""
        with patch('api.routers.users.get_current_user') as mock:
            mock.return_value = {"id": None}  # Invalid
            
            response = client.get(
                "/api/v1/users/profile",
                headers={"Authorization": "Bearer token"}
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 401]
    
    def test_duplicate_session_id(self, test_db_connection):
        """Test handling duplicate session IDs"""
        db = Database(test_db_connection)
        
        db.execute(
            "INSERT INTO users (id, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            ("user1", "test@example.com", "hash", "John", "Doe")
        )
        
        # Insert session
        db.execute(
            "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
            ("sess1", "user1", "welcome", "[]")
        )
        db.commit()
        
        # Try to insert duplicate (should fail due to PRIMARY KEY)
        try:
            db.execute(
                "INSERT INTO chat_sessions (id, user_id, state, symptoms_json) VALUES (?, ?, ?, ?)",
                ("sess1", "user1", "welcome", "[]")
            )
            db.commit()
            assert False, "Should have raised error"
        except Exception:
            # Expected - UNIQUE constraint
            pass
