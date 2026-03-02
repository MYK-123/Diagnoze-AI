#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.db_models import (
    User, SessionToken, ChatSession, ChatMessage, ChatHistory,
    _now, _json_dumps, _json_loads
)


class TestJsonHelpers(unittest.TestCase):
    """Test JSON helper functions"""

    def test_now_returns_iso_string(self):
        """Test that _now returns ISO format string"""
        result = _now()
        self.assertIsInstance(result, str)
        # Should be parseable as ISO datetime
        datetime.fromisoformat(result)

    def test_json_dumps_serializes_dict(self):
        """Test JSON dumps function"""
        data = {"key": "value", "num": 42}
        result = _json_dumps(data)
        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), data)

    def test_json_dumps_serializes_list(self):
        """Test JSON dumps with list"""
        data = ["item1", "item2", "item3"]
        result = _json_dumps(data)
        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), data)

    def test_json_dumps_handles_special_chars(self):
        """Test JSON dumps preserves special characters"""
        data = {"text": "Hello, world! 你好"}
        result = _json_dumps(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["text"], data["text"])

    def test_json_loads_deserializes_string(self):
        """Test JSON loads function"""
        json_str = '{"key": "value"}'
        result = _json_loads(json_str)
        self.assertEqual(result, {"key": "value"})

    def test_json_loads_returns_none_for_empty(self):
        """Test JSON loads returns None for empty string"""
        result = _json_loads("")
        self.assertIsNone(result)

    def test_json_loads_returns_none_for_none(self):
        """Test JSON loads returns None for None input"""
        result = _json_loads(None)
        self.assertIsNone(result)

    def test_json_loads_deserializes_list(self):
        """Test JSON loads with list"""
        json_str = '["item1", "item2"]'
        result = _json_loads(json_str)
        self.assertEqual(result, ["item1", "item2"])


class TestUser(unittest.TestCase):
    """Test User model"""

    def test_user_init(self):
        """Test User initialization"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        self.assertEqual(user.id, "user1")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "John")

    def test_user_init_with_defaults(self):
        """Test User initialization with default values"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        self.assertEqual(user.age, 18)
        self.assertEqual(user.gender, "prefer_not_to_say")
        self.assertEqual(user.account_type, "user")
        self.assertTrue(user.is_active)

    def test_user_init_with_custom_values(self):
        """Test User initialization with custom values"""
        user = User(
            id="admin1",
            email="admin@example.com",
            password_hash="hashed",
            first_name="Admin",
            last_name="User",
            age=30,
            gender="Male",
            account_type="admin",
            phone="1234567890"
        )
        self.assertEqual(user.age, 30)
        self.assertEqual(user.gender, "Male")
        self.assertEqual(user.account_type, "admin")
        self.assertEqual(user.phone, "1234567890")

    def test_user_created_at_auto_set(self):
        """Test that created_at is auto-set if not provided"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        self.assertIsNotNone(user.created_at)

    def test_user_to_public_dict(self):
        """Test User.to_public_dict method"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe"
        )
        public_dict = user.to_public_dict()
        
        self.assertIn("id", public_dict)
        self.assertIn("email", public_dict)
        self.assertIn("first_name", public_dict)
        self.assertNotIn("password_hash", public_dict)

    def test_user_to_public_dict_includes_preferences(self):
        """Test that public dict includes preferences"""
        user = User(
            id="user1",
            email="test@example.com",
            password_hash="hashed",
            first_name="John",
            last_name="Doe",
            preferences_json='{"theme": "dark"}'
        )
        public_dict = user.to_public_dict()
        self.assertIn("preferences", public_dict)
        self.assertEqual(public_dict["preferences"]["theme"], "dark")

    def test_user_from_db_row(self):
        """Test User.from_db_row class method"""
        row = {
            "id": "user1",
            "email": "test@example.com",
            "password_hash": "hashed",
            "first_name": "John",
            "last_name": "Doe",
            "age": 25,
            "gender": "Male",
            "account_type": "user",
            "phone": "1234567890",
            "preferences_json": "{}",
            "created_at": "2024-01-01T00:00:00",
            "last_login": "2024-03-01T00:00:00",
            "is_active": 1
        }
        user = User.from_db_row(row)
        
        self.assertEqual(user.id, "user1")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.age, 25)

    def test_user_from_db_row_handles_missing_fields(self):
        """Test User.from_db_row with missing optional fields"""
        row = {
            "id": "user1",
            "email": "test@example.com",
            "password_hash": "hashed",
            "first_name": "John",
            "last_name": "Doe",
            "age": 25,
            "gender": "Male",
            "account_type": "user",
            "is_active": 1
        }
        user = User.from_db_row(row)
        
        self.assertIsNone(user.phone)
        self.assertIsNone(user.last_login)


class TestSessionToken(unittest.TestCase):
    """Test SessionToken model"""

    def test_session_token_init(self):
        """Test SessionToken initialization"""
        token = SessionToken(
            token="tok_123",
            user_id="user1"
        )
        self.assertEqual(token.token, "tok_123")
        self.assertEqual(token.user_id, "user1")

    def test_session_token_created_at_auto_set(self):
        """Test SessionToken created_at is auto-set"""
        token = SessionToken(
            token="tok_123",
            user_id="user1"
        )
        self.assertIsNotNone(token.created_at)

    def test_session_token_new_token_generates_unique(self):
        """Test SessionToken.new_token generates unique tokens"""
        token1 = SessionToken.new_token()
        token2 = SessionToken.new_token()
        
        self.assertNotEqual(token1, token2)
        self.assertTrue(token1.startswith("tok_"))
        self.assertTrue(token2.startswith("tok_"))

    def test_session_token_new_token_format(self):
        """Test SessionToken.new_token returns correct format"""
        token = SessionToken.new_token()
        self.assertIsInstance(token, str)
        self.assertTrue(token.startswith("tok_"))
        self.assertGreater(len(token), 10)

    def test_session_token_from_db_row(self):
        """Test SessionToken.from_db_row"""
        row = {
            "token": "tok_123",
            "user_id": "user1",
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T01:00:00"
        }
        token = SessionToken.from_db_row(row)
        
        self.assertEqual(token.token, "tok_123")
        self.assertEqual(token.user_id, "user1")
        self.assertEqual(token.created_at, "2024-01-01T00:00:00")


class TestChatSession(unittest.TestCase):
    """Test ChatSession model"""

    def test_chat_session_init(self):
        """Test ChatSession initialization"""
        session = ChatSession(
            id="session1",
            user_id="user1"
        )
        self.assertEqual(session.id, "session1")
        self.assertEqual(session.user_id, "user1")
        self.assertEqual(session.state, "welcome")

    def test_chat_session_symptoms_empty(self):
        """Test ChatSession.symptoms returns empty list"""
        session = ChatSession(
            id="session1",
            user_id="user1"
        )
        symptoms = session.symptoms()
        self.assertEqual(symptoms, [])

    def test_chat_session_symptoms_with_data(self):
        """Test ChatSession.symptoms with data"""
        session = ChatSession(
            id="session1",
            user_id="user1",
            symptoms_json='["headache", "fever"]'
        )
        symptoms = session.symptoms()
        self.assertEqual(symptoms, ["headache", "fever"])

    def test_chat_session_set_symptoms(self):
        """Test ChatSession.set_symptoms"""
        session = ChatSession(
            id="session1",
            user_id="user1"
        )
        session.set_symptoms(["fever", "headache", "cough"])
        
        symptoms = session.symptoms()
        self.assertEqual(len(symptoms), 3)
        self.assertIn("fever", symptoms)

    def test_chat_session_set_symptoms_deduplicates(self):
        """Test ChatSession.set_symptoms deduplicates"""
        session = ChatSession(
            id="session1",
            user_id="user1"
        )
        session.set_symptoms(["fever", "fever", "headache"])
        
        symptoms = session.symptoms()
        self.assertEqual(len(symptoms), 2)

    def test_chat_session_set_symptoms_sorts(self):
        """Test ChatSession.set_symptoms sorts"""
        session = ChatSession(
            id="session1",
            user_id="user1"
        )
        session.set_symptoms(["zebra", "apple", "monkey"])
        
        symptoms = session.symptoms()
        self.assertEqual(symptoms, sorted(["zebra", "apple", "monkey"]))

    def test_chat_session_from_db_row(self):
        """Test ChatSession.from_db_row"""
        row = {
            "id": "session1",
            "user_id": "user1",
            "created_at": "2024-01-01T00:00:00",
            "last_activity": "2024-01-01T01:00:00",
            "state": "symptoms",
            "symptoms_json": '["headache"]'
        }
        session = ChatSession.from_db_row(row)
        
        self.assertEqual(session.id, "session1")
        self.assertEqual(session.state, "symptoms")


class TestChatMessage(unittest.TestCase):
    """Test ChatMessage model"""

    def test_chat_message_init(self):
        """Test ChatMessage initialization"""
        msg = ChatMessage(
            session_id="session1",
            role="user",
            content="I have a headache"
        )
        self.assertEqual(msg.session_id, "session1")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "I have a headache")

    def test_chat_message_timestamp_auto_set(self):
        """Test ChatMessage timestamp is auto-set"""
        msg = ChatMessage(
            session_id="session1",
            role="user",
            content="I have a headache"
        )
        self.assertIsNotNone(msg.timestamp)

    def test_chat_message_to_dict(self):
        """Test ChatMessage.to_dict"""
        msg = ChatMessage(
            session_id="session1",
            role="user",
            content="I have a headache"
        )
        msg_dict = msg.to_dict()
        
        self.assertIn("role", msg_dict)
        self.assertIn("content", msg_dict)
        self.assertIn("timestamp", msg_dict)
        self.assertEqual(msg_dict["role"], "user")

    def test_chat_message_to_dict_with_data(self):
        """Test ChatMessage.to_dict with data"""
        msg = ChatMessage(
            session_id="session1",
            role="assistant",
            content="You might have migraine",
            data_json='{"confidence": 0.85}'
        )
        msg_dict = msg.to_dict()
        
        self.assertIn("data", msg_dict)
        self.assertEqual(msg_dict["data"]["confidence"], 0.85)

    def test_chat_message_from_db_row(self):
        """Test ChatMessage.from_db_row"""
        row = {
            "session_id": "session1",
            "role": "user",
            "content": "I have a headache",
            "id": 1,
            "timestamp": "2024-01-01T00:00:00",
            "data_json": None
        }
        msg = ChatMessage.from_db_row(row)
        
        self.assertEqual(msg.session_id, "session1")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.id, 1)


class TestChatHistory(unittest.TestCase):
    """Test ChatHistory model"""

    def test_chat_history_init(self):
        """Test ChatHistory initialization"""
        history = ChatHistory(
            id="chat1",
            user_id="user1",
            title="Chat on 2024-01-01"
        )
        self.assertEqual(history.id, "chat1")
        self.assertEqual(history.user_id, "user1")
        self.assertEqual(history.title, "Chat on 2024-01-01")

    def test_chat_history_to_dict(self):
        """Test ChatHistory.to_dict"""
        history = ChatHistory(
            id="chat1",
            user_id="user1",
            title="Chat Session",
            created_at="2024-01-01T10:00:00",
            symptoms_json='["headache", "fever"]',
            predictions_json='["migraine"]',
            messages_json='[]'
        )
        hist_dict = history.to_dict()
        
        self.assertIn("id", hist_dict)
        self.assertIn("user_id", hist_dict)
        self.assertIn("title", hist_dict)
        self.assertIn("symptoms", hist_dict)
        self.assertIn("predictions", hist_dict)
        self.assertIn("messages", hist_dict)

    def test_chat_history_to_dict_extracts_date(self):
        """Test ChatHistory.to_dict extracts date from created_at"""
        history = ChatHistory(
            id="chat1",
            user_id="user1",
            title="Chat Session",
            created_at="2024-01-15T10:30:00"
        )
        hist_dict = history.to_dict()
        
        self.assertEqual(hist_dict["date"], "2024-01-15")

    def test_chat_history_from_db_row(self):
        """Test ChatHistory.from_db_row"""
        row = {
            "id": "chat1",
            "user_id": "user1",
            "title": "Chat Session",
            "created_at": "2024-01-01T10:00:00",
            "ended_at": "2024-01-01T11:00:00",
            "duration": "1h",
            "symptoms_json": "[]",
            "predictions_json": "[]",
            "messages_json": "[]"
        }
        history = ChatHistory.from_db_row(row)
        
        self.assertEqual(history.id, "chat1")
        self.assertEqual(history.duration, "1h")

    def test_chat_history_from_db_row_handles_missing(self):
        """Test ChatHistory.from_db_row handles missing fields"""
        row = {
            "id": "chat1",
            "user_id": "user1",
            "title": "Chat Session"
        }
        history = ChatHistory.from_db_row(row)
        
        self.assertEqual(history.id, "chat1")
        self.assertEqual(history.duration, "N/A")


if __name__ == '__main__':
    unittest.main()
