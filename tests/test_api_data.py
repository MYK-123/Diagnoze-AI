#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.data import (
    init_dummy_data, create_token, create_user_id, 
    create_chat_id, create_session_id, users_db, symptoms_db,
    diseases_db, medical_symptoms_db, medical_diseases_db
)


class TestDummyDataInitialization(unittest.TestCase):
    """Test dummy data initialization"""

    def test_init_dummy_data(self):
        """Test initializing dummy data"""
        init_dummy_data()
        self.assertGreater(len(users_db), 0)
        self.assertGreater(len(symptoms_db), 0)
        self.assertGreater(len(diseases_db), 0)

    def test_users_data_populated(self):
        """Test that users data is populated"""
        init_dummy_data()
        self.assertIn("user1@example.com", users_db)
        self.assertIn("admin@diagnoze.ai", users_db)

    def test_user_data_structure(self):
        """Test user data structure"""
        init_dummy_data()
        user = users_db["user1@example.com"]
        required_fields = ["id", "email", "password_hash", "first_name", "last_name"]
        for field in required_fields:
            self.assertIn(field, user)

    def test_symptoms_data_populated(self):
        """Test that symptoms data is populated"""
        init_dummy_data()
        self.assertIn("headache", symptoms_db)
        self.assertIn("fever", symptoms_db)

    def test_symptom_data_structure(self):
        """Test symptom data structure"""
        init_dummy_data()
        symptom = symptoms_db["headache"]
        required_fields = ["id", "name", "category", "description"]
        for field in required_fields:
            self.assertIn(field, symptom)

    def test_diseases_data_populated(self):
        """Test that diseases data is populated"""
        init_dummy_data()
        self.assertIn("migraine", diseases_db)
        self.assertIn("viral_infection", diseases_db)

    def test_disease_data_structure(self):
        """Test disease data structure"""
        init_dummy_data()
        disease = diseases_db["migraine"]
        required_fields = ["id", "name", "category", "description"]
        for field in required_fields:
            self.assertIn(field, disease)

    def test_medical_symptoms_populated(self):
        """Test that medical symptoms list is populated"""
        init_dummy_data()
        self.assertGreater(len(medical_symptoms_db), 0)

    def test_medical_diseases_populated(self):
        """Test that medical diseases list is populated"""
        init_dummy_data()
        self.assertGreater(len(medical_diseases_db), 0)


class TestTokenGeneration(unittest.TestCase):
    """Test token generation functions"""

    def test_create_token(self):
        """Test token creation"""
        token = create_token()
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertIn("token_", token)

    def test_tokens_unique(self):
        """Test that tokens are unique"""
        token1 = create_token()
        token2 = create_token()
        self.assertNotEqual(token1, token2)

    def test_create_user_id(self):
        """Test user ID creation"""
        user_id = create_user_id()
        self.assertIsNotNone(user_id)
        self.assertIsInstance(user_id, str)
        self.assertIn("user_", user_id)

    def test_user_ids_unique(self):
        """Test that user IDs are unique"""
        id1 = create_user_id()
        id2 = create_user_id()
        self.assertNotEqual(id1, id2)

    def test_create_chat_id(self):
        """Test chat ID creation"""
        chat_id = create_chat_id()
        self.assertIsNotNone(chat_id)
        self.assertIsInstance(chat_id, str)
        self.assertIn("chat_", chat_id)

    def test_chat_ids_unique(self):
        """Test that chat IDs are unique"""
        id1 = create_chat_id()
        id2 = create_chat_id()
        self.assertNotEqual(id1, id2)

    def test_create_session_id(self):
        """Test session ID creation"""
        session_id = create_session_id()
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
        self.assertIn("session_", session_id)

    def test_session_ids_unique(self):
        """Test that session IDs are unique"""
        id1 = create_session_id()
        id2 = create_session_id()
        self.assertNotEqual(id1, id2)


if __name__ == '__main__':
    unittest.main()
