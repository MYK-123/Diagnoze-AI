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
