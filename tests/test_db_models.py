import pytest
from datetime import datetime
import json

from api.db_models import (
    User,
    SessionToken,
    ChatSession,
    ChatMessage,
    ChatHistory,
    _json_dumps,
    _json_loads
)


class TestJsonUtilities:
    """Tests for JSON utility functions"""
    
    def test_json_dumps_dict(self):
        """Test JSON dumps with dictionary"""
        data = {"key": "value", "number": 42}
        result = _json_dumps(data)
        
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    def test_json_dumps_list(self):
        """Test JSON dumps with list"""
        data = ["item1", "item2", 123]
        result = _json_dumps(data)
        
        assert isinstance(result, str)
        assert "item1" in result

    def test_json_dumps_unicode(self):
        """Test JSON dumps with unicode characters"""
        data = {"name": "测试", "emoji": "😀"}
        result = _json_dumps(data)
        
        assert isinstance(result, str)
        assert "测试" in result

    def test_json_loads_valid_json(self):
        """Test JSON loads with valid JSON string"""
        json_str = '{"key": "value"}'
        result = _json_loads(json_str)
        
        assert isinstance(result, dict)
        assert result["key"] == "value"

    def test_json_loads_none(self):
        """Test JSON loads with None"""
        result = _json_loads(None)
        
        assert result is None

    def test_json_loads_empty_string(self):
        """Test JSON loads with empty string"""
        result = _json_loads("")
        
        assert result is None

    def test_json_round_trip(self):
        """Test round trip JSON dumps and loads"""
        original = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        dumped = _json_dumps(original)
        loaded = _json_loads(dumped)
        
        assert loaded == original


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
            age=30,
            gender="male",
            account_type="user"
        )
        
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.is_active is True

    def test_user_to_public_dict(self):
        """Test converting user to public dictionary"""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash_value",
            first_name="John",
            last_name="Doe",
            age=30,
            gender="male",
            account_type="user",
            phone="1234567890"
        )
        user.created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        public_dict = user.to_public_dict()
        
        assert public_dict["id"] == "user123"
        assert public_dict["email"] == "test@example.com"
        assert public_dict["first_name"] == "John"
        assert "password_hash" not in public_dict
        assert public_dict["phone"] == "1234567890"

    def test_user_preferences_json(self):
        """Test user preferences JSON handling"""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash_value",
            first_name="John",
            last_name="Doe"
        )
        
        prefs = {"theme": "dark", "notifications": True}
        user.preferences_json = _json_dumps(prefs)
        
        loaded_prefs = _json_loads(user.preferences_json)
        assert loaded_prefs == prefs


class TestSessionTokenModel:
    """Tests for SessionToken model"""
    
    def test_session_token_creation(self):
        """Test creating a session token"""
        token = SessionToken(
            token="tok_test123",
            user_id="user123",
            expires_at=datetime(2025, 12, 31)
        )
        
        assert token.token == "tok_test123"
        assert token.user_id == "user123"

    def test_session_token_new_token(self):
        """Test generating a new token"""
        token = SessionToken.new_token()
        
        assert token.startswith("tok_")
        assert len(token) > 4

    def test_session_token_unique_tokens(self):
        """Test that generated tokens are unique"""
        token1 = SessionToken.new_token()
        token2 = SessionToken.new_token()
        
        assert token1 != token2


class TestChatSessionModel:
    """Tests for ChatSession model"""
    
    def test_chat_session_creation(self):
        """Test creating a chat session"""
        session = ChatSession(
            id="session_123",
            user_id="user123",
            state="welcome"
        )
        
        assert session.id == "session_123"
        assert session.user_id == "user123"
        assert session.state == "welcome"
        assert session.symptoms_json == "[]"

    def test_chat_session_symptoms_getter(self):
        """Test getting symptoms from chat session"""
        session = ChatSession(
            id="session_123",
            user_id="user123"
        )
        session.symptoms_json = _json_dumps(["headache", "fever"])
        
        symptoms = session.symptoms()
        
        assert symptoms == ["headache", "fever"]

    def test_chat_session_symptoms_setter(self):
        """Test setting symptoms in chat session"""
        session = ChatSession(
            id="session_123",
            user_id="user123"
        )
        
        session.set_symptoms(["cough", "sore throat", "fever"])
        
        symptoms = session.symptoms()
        assert "cough" in symptoms
        assert "sore throat" in symptoms
        assert "fever" in symptoms

    def test_chat_session_symptoms_deduplication(self):
        """Test that duplicate symptoms are removed"""
        session = ChatSession(
            id="session_123",
            user_id="user123"
        )
        
        session.set_symptoms(["headache", "headache", "fever"])
        
        symptoms = session.symptoms()
        assert symptoms.count("headache") == 1

    def test_chat_session_symptoms_sorted(self):
        """Test that symptoms are sorted"""
        session = ChatSession(
            id="session_123",
            user_id="user123"
        )
        
        session.set_symptoms(["zebra", "apple", "monkey"])
        
        symptoms = session.symptoms()
        assert symptoms == sorted(symptoms)


class TestChatMessageModel:
    """Tests for ChatMessage model"""
    
    def test_chat_message_creation(self):
        """Test creating a chat message"""
        message = ChatMessage(
            session_id="session_123",
            role="user",
            content="Hello, how are you?"
        )
        
        assert message.session_id == "session_123"
        assert message.role == "user"
        assert message.content == "Hello, how are you?"

    def test_chat_message_to_dict(self):
        """Test converting chat message to dictionary"""
        message = ChatMessage(
            session_id="session_123",
            role="assistant",
            content="I'm doing well, thank you!"
        )
        message.timestamp = datetime(2023, 6, 15, 10, 30, 0)
        
        message_dict = message.to_dict()
        
        assert message_dict["role"] == "assistant"
        assert message_dict["content"] == "I'm doing well, thank you!"
        assert "timestamp" in message_dict
        assert message_dict["data"] == {}

    def test_chat_message_with_data(self):
        """Test chat message with data payload"""
        message = ChatMessage(
            session_id="session_123",
            role="assistant",
            content="Here are predictions"
        )
        data = {"predictions": [{"name": "Flu", "confidence": 0.8}]}
        message.data_json = _json_dumps(data)
        
        message_dict = message.to_dict()
        
        assert message_dict["data"]["predictions"][0]["name"] == "Flu"


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
        assert history.user_id == "user123"
        assert history.title == "My Chat"

    def test_chat_history_to_dict(self):
        """Test converting chat history to dictionary"""
        history = ChatHistory(
            id="chat_123",
            user_id="user123",
            title="Symptom Analysis"
        )
        history.created_at = datetime(2023, 6, 15, 10, 0, 0)
        history.ended_at = datetime(2023, 6, 15, 10, 30, 0)
        history.symptoms_json = _json_dumps(["headache", "fever"])
        history.predictions_json = _json_dumps([{"name": "Cold", "confidence": 0.75}])
        
        history_dict = history.to_dict()
        
        assert history_dict["id"] == "chat_123"
        assert history_dict["user_id"] == "user123"
        assert history_dict["title"] == "Symptom Analysis"
        assert "2023-06-15" in history_dict["date"]
        assert len(history_dict["symptoms"]) == 2
        assert len(history_dict["predictions"]) == 1

    def test_chat_history_with_messages(self):
        """Test chat history with messages"""
        history = ChatHistory(
            id="chat_123",
            user_id="user123",
            title="Test Chat"
        )
        messages = [
            {"role": "user", "content": "I have a headache"},
            {"role": "assistant", "content": "I understand"}
        ]
        history.messages_json = _json_dumps(messages)
        
        history_dict = history.to_dict()
        
        assert len(history_dict["messages"]) == 2
        assert history_dict["messages"][0]["role"] == "user"
