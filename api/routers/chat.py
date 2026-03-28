from datetime import datetime
import secrets
import json
import sqlite3
import logging

from fastapi import APIRouter, Depends, HTTPException
from ..auth_db import get_current_user
from db.core import get_db
from ..database import Database
from ..db_models import ChatHistory, ChatMessage as DBChatMessage, ChatSession
from ..models.schemas import ChatMessage, PredictionRequest, SaveChatSessionRequest
from ..models.responses import success_response, chat_response
from typing import Any

# Import core modules
from core.core import get_top_k_diseases_from_prediction_with_probablities
from core.symptoms import get_all_symptoms_cache

router = APIRouter()
logger = logging.getLogger("diagnoze.chat")

# Emergency keywords for safety check
EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "severe bleeding",
    "cannot breathe", "heart attack", "stroke", "unconscious",
    "severe chest", "breathe", "bleeding", "emergency"
]

@router.post("/start-session", summary="Start new chat session")
async def start_chat_session(user: dict[str, Any] = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Start a new chat session"""
    db = Database(conn)
    session_id = f"session_{secrets.token_hex(8)}"
    now = datetime.now().isoformat()
    # Normalize user id
    uid = user.get("user_id") if user.get("user_id") is not None else user.get("id")
    logger.info("Starting chat session for user dict=%s normalized_user_id=%s", user, uid)
    db.execute(
        """
        INSERT INTO chat_sessions (id, user_id, created_at, last_activity, state, symptoms_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, uid, now, now, "welcome", "[]")
    )
    db.commit()

    return success_response({
        "session_id": session_id,
        "message": "Hello! I'm Diagnoze AI. Describe your symptoms and I'll help analyze possible conditions."
    })

@router.post("/send-message", summary="Send chat message")
async def send_chat_message(
    chat_data: ChatMessage,
    user: dict[str, Any] = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Send message in chat session"""
    db = Database(conn)
    # Normalize user id
    uid = user.get("user_id") if user.get("user_id") is not None else user.get("id")
    logger.info("Authenticated user dict=%s normalized_user_id=%s", user, uid)
    
    sess_row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", (chat_data.session_id,))
    logger.info("Chat session lookup result: %s", sess_row)
    if not sess_row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    sess = ChatSession.from_db_row(sess_row)
    logger.info("Comparing session.user_id=%s (%s) with token user_id=%s (%s)", sess.user_id, type(sess.user_id), uid, type(uid))
    # Compare as strings to avoid mismatches between int and str stored in DB
    if str(sess.user_id) != str(uid):
        logger.warning("Access denied: session belongs to %s but token user is %s", sess.user_id, uid)
        raise HTTPException(status_code=403, detail="Access denied")

    now = datetime.now().isoformat()
    db.execute(
        "UPDATE chat_sessions SET last_activity = ? WHERE id = ?",
        (now, sess.id)
    )

    # Add user message
    db.execute(
        """
        INSERT INTO chat_messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (sess.id, "user", chat_data.message, now)
    )

    # Add symptoms if provided
    if chat_data.symptoms:
        current = sess.symptoms()
        current.extend(chat_data.symptoms)
        sess.set_symptoms(current)
        db.execute(
            "UPDATE chat_sessions SET symptoms_json = ? WHERE id = ?",
            (sess.symptoms_json, sess.id)
        )
    
    logger.debug("DEBUG: send Message 3: %s", chat_data.message)
    logger.debug("DEBUG: send Message 3 Sympt: %s", chat_data.symptoms)

    # Generate AI response using core prediction engine
    session_view: dict[str, Any] = {"state": sess.state, "symptoms": sess.symptoms()}
    response: dict[str, Any] = generate_ai_response(chat_data.message, session_view)
    response_data: dict[str, Any] = response.get("data", {})

    logger.debug("DEBUG: send Message 4: %s", chat_data.message)

    # Persist assistant message with extra data payload
    extra: dict[str, Any] = {k: v for k, v in response.items() if k != "response"}
    db.execute(
        """
        INSERT INTO chat_messages (session_id, role, content, timestamp, data_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            sess.id,
            "assistant",
            response_data.get("response", ""),
            now,
            json.dumps(extra, ensure_ascii=False) if extra else None
        )
    )

    logger.debug("DEBUG: send Message 5: %s", chat_data.message)

    if response_data.get("next_state"):
        db.execute(
            "UPDATE chat_sessions SET state = ? WHERE id = ?",
            (response_data["next_state"], sess.id)
        )

    db.commit()

    logger.debug("DEBUG: send Message 6: %s", chat_data.message)

    return response

def generate_ai_response(user_input: str, session: dict[str, Any]) -> dict[str, Any]:
    """Generate AI response based on user input and session state using core prediction"""
    
    current_state: str = session["state"]
    symptoms: list[str] = session["symptoms"]
    
    # Convert user input to lowercase for matching
    input_lower = user_input.lower()
    
    # Check for emergency keywords
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in input_lower:
            return chat_response(
                response_text="⚠️ EMERGENCY WARNING ⚠️\n\nBased on your symptoms, you may need immediate medical attention. Please call emergency services or go to the nearest hospital immediately.",
                emergency={
                    "level": "critical",
                    "message": "Potential emergency condition detected",
                    "action": "Call emergency services immediately",
                    "numbers": ["108", "102", "112"]
                }
            )
    
    try:
        symptoms_cache = get_all_symptoms_cache()
        all_symptoms_list = symptoms_cache.get_all_list()
        logger.debug("INFO: all symptoms count: %s", symptoms_cache.size())
        logger.debug("INFO: all symptoms count: %s", len(all_symptoms_list))

        new_symptoms: list[str] = []
        for symptom in all_symptoms_list:
            symptom_name = symptom.get_name().lower()
            if symptom_name in input_lower or input_lower in symptom_name:
                logger.debug("INFO: Adding symptom: %s, with actual: %s", symptom_name, symptom.get_name())
                new_symptoms.append(symptom.get_name())
        
        if new_symptoms:
            symptoms = list(set(symptoms + new_symptoms))
        print(f"SYMPTOMS FOUND: {symptoms}")
    except Exception as e:
        print(f"Error extracting symptoms: {e}")
    
    logger.debug("INFO: Current state: %s, Symptoms: %s", current_state, symptoms)

    # if current_state == "welcome" or len(symptoms) < 2:
    #     return chat_response(
    #         response_text="Thank you for sharing. Could you tell me more about your symptoms? What else are you experiencing?",
    #         question={
    #             "id": "follow_up_1",
    #             "text": "Are there any other symptoms you're experiencing?"
    #         },
    #         symptoms=symptoms
    #     )
    
    # elif current_state == "collecting_symptoms" and len(symptoms) >= 2:
    #     try:
    #         predictions: list[dict[str, Any]] = generate_predictions_from_core(symptoms)
            
    #         if not predictions:
    #             return chat_response(
    #                 response_text="I couldn't find matching conditions for these symptoms. Could you provide more details or additional symptoms?",
    #                 symptoms=symptoms
    #             )
            
    #         return chat_response(
    #             response_text="Based on your symptoms, here are possible conditions I've identified:",
    #             predictions=predictions,
    #             symptoms=symptoms
    #         )
    #     except Exception as e:
    #         print(f"Error generating predictions: {e}")
    #         return chat_response(
    #             response_text="I encountered an error analyzing your symptoms. Please try again.",
    #             symptoms=symptoms
    #         )
        
    try:
        print(f"SYMPTOMS FOUND: {symptoms}")
        predictions: list[dict[str, Any]] = generate_predictions_from_core(symptoms)
        
        if not predictions:
            return chat_response(
                response_text="I couldn't find matching conditions for these symptoms. Could you provide more details or additional symptoms?",
                symptoms=symptoms
            )
        
        return chat_response(
            response_text="Based on your symptoms, here are possible conditions I've identified:",
            predictions=predictions,
            symptoms=symptoms
        )
    except Exception as e:
        print(f"Error generating predictions: {e}")
        return chat_response(
            response_text="I encountered an error analyzing your symptoms. Please try again.",
            symptoms=symptoms
        )
    
    return chat_response(
        response_text="I understand. Could you please provide more details about your symptoms?",
        symptoms=symptoms
    )

def generate_predictions_from_core(symptom_names: list[str]) -> list[dict[str, Any]]:
    """Generate disease predictions using core prediction engine"""
    try:
        symptoms_cache = get_all_symptoms_cache()
        all_symptoms_list = symptoms_cache.get_all_list()
        
        symptom_objects: list[Any] = []
        for symptom_name in symptom_names:
            for symptom in all_symptoms_list:
                if symptom.get_name().lower() == symptom_name.lower():
                    symptom_objects.append(symptom)
                    break
        
        if not symptom_objects:
            return []
        
        predictions = get_top_k_diseases_from_prediction_with_probablities(
            include_symptoms=symptom_objects,
            exclude_symptoms=None,
            top_k=3
        )
        
        if not predictions:
            return []
        
        formatted_predictions: list[dict[str, Any]] = []
        for disease, confidence in predictions:
            confidence_percent = min(95, int(confidence * 100))
            
            formatted_predictions.append({
                "id": disease.get_disease_id(),
                "name": disease.get_disease_name(),
                "confidence": confidence_percent,
                "matching_symptoms": symptom_names[:3],
                "category": disease.get_category(),
                "severity": disease.get_severity_level_str(),
                "emergency": disease.get_severity_level_str().lower() == "high"
            })
        
        return formatted_predictions
    except Exception as e:
        print(f"Error in core prediction: {e}")
        return []

@router.post("/generate-prediction", summary="Generate predictions from symptoms")
async def generate_prediction(
    prediction_data: PredictionRequest,
    user: dict[str, Any] = Depends(get_current_user)
):
    """Generate disease predictions from symptoms list"""
    try:
        symptom_names: list[str] = [symptom.name if hasattr(symptom, 'name') else str(symptom) for symptom in prediction_data.symptoms]
        
        predictions: list[dict[str, Any]] = generate_predictions_from_core(symptom_names)
        
        return success_response({
            "predictions": predictions,
            "symptoms_analyzed": symptom_names,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@router.post("/save-session", summary="Save chat session")
async def save_chat_session(
    payload: SaveChatSessionRequest,
    user: dict[str, Any] = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Save chat session to history"""
    db = Database(conn)
    
    sess_row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", (payload.session_id,))
    if not sess_row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    sess = ChatSession.from_db_row(sess_row)
    
    if sess.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    symptoms = sess.symptoms()
    title = payload.title
    if not title:
        title = f"Chat about {', '.join(symptoms[:3])}" if symptoms else "Chat Session"
        if symptoms and len(symptoms) > 3:
            title += f" and {len(symptoms)-3} more"

    msgs_rows = db.fetch_all(
        """
        SELECT * FROM chat_messages WHERE session_id = ?
        ORDER BY id ASC
        """,
        (sess.id,)
    )
    
    messages_list: list[dict[str, Any]] = [DBChatMessage.from_db_row(row).to_dict() for row in msgs_rows]

    predictions: list[Any] = []
    for msg_row in reversed(msgs_rows):
        msg = DBChatMessage.from_db_row(msg_row)
        if msg.role == "assistant" and msg.data_json:
            try:
                data: Any = json.loads(msg.data_json)
                if isinstance(data, dict):
                    inner: Any = data.get("data", data)
                    if isinstance(inner, dict) and inner.get("predictions"):
                        predictions = inner["predictions"]
                        break
            except Exception:
                continue

    chat_id = f"chat_{secrets.token_hex(8)}"
    now = datetime.now().isoformat()
    
    db.execute(
        """
        INSERT INTO chat_history (
            id, user_id, title, created_at, ended_at, duration,
            symptoms_json, predictions_json, messages_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id, user["user_id"], title, sess.created_at, now, "N/A",
            json.dumps(symptoms, ensure_ascii=False),
            json.dumps(predictions or [], ensure_ascii=False),
            json.dumps(messages_list, ensure_ascii=False)
        )
    )

    db.execute("DELETE FROM chat_messages WHERE session_id = ?", (sess.id,))
    db.execute("DELETE FROM chat_sessions WHERE id = ?", (sess.id,))
    db.commit()

    return success_response({"chat_id": chat_id, "title": title, "message": "Chat saved successfully"})

@router.get("/session/{session_id}", summary="Get chat session")
async def get_chat_session(session_id: str, user: dict[str, Any] = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Get chat session by ID"""
    db = Database(conn)
    
    sess_row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    if not sess_row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    sess = ChatSession.from_db_row(sess_row)
    
    if sess.user_id != user["user_id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    msgs_rows = db.fetch_all(
        """
        SELECT * FROM chat_messages WHERE session_id = ?
        ORDER BY id ASC
        """,
        (sess.id,)
    )
    
    return success_response(
        {
            "id": sess.id,
            "user_id": sess.user_id,
            "created_at": sess.created_at,
            "last_activity": sess.last_activity,
            "state": sess.state,
            "symptoms": sess.symptoms(),
            "messages": [DBChatMessage.from_db_row(row).to_dict() for row in msgs_rows],
        }
    )

@router.delete("/session/{session_id}", summary="Delete chat session")
async def delete_chat_session(session_id: str, user: dict[str, Any] = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Delete chat session"""
    db = Database(conn)
    
    sess_row = db.fetch_one("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    if not sess_row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    sess = ChatSession.from_db_row(sess_row)
    
    if sess.user_id != user["user_id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.execute("DELETE FROM chat_sessions WHERE id = ?", (sess.id,))
    db.commit()
    
    return success_response(message="Chat session deleted")

