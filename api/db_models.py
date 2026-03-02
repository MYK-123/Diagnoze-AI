from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
import json
import secrets

def _now() -> str:
    """Get current UTC datetime as ISO string"""
    return datetime.utcnow().isoformat()

def _json_dumps(value: Any) -> str:
    """Serialize value to JSON string"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

def _json_loads(value: Optional[str]) -> Any:
    """Deserialize JSON string to value"""
    if not value:
        return None
    return json.loads(value)

class User:
    """User model"""
    
    def __init__(
        self,
        id: str,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        age: int = 18,
        gender: str = "prefer_not_to_say",
        account_type: str = "user",
        phone: Optional[str] = None,
        preferences_json: str = "{}",
        created_at: Optional[str] = None,
        last_login: Optional[str] = None,
        is_active: bool = True,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.account_type = account_type
        self.phone = phone
        self.preferences_json = preferences_json
        self.created_at = created_at or _now()
        self.last_login = last_login
        self.is_active = is_active
    
    def to_public_dict(self) -> dict:
        """Convert to public dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "gender": self.gender,
            "account_type": self.account_type,
            "phone": self.phone,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "preferences": _json_loads(self.preferences_json) or {},
            "is_active": self.is_active,
        }
    
    @staticmethod
    def from_db_row(row: dict) -> User:
        """Create User from database row"""
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            age=row["age"],
            gender=row["gender"],
            account_type=row["account_type"],
            phone=row.get("phone"),
            preferences_json=row.get("preferences_json", "{}"),
            created_at=row.get("created_at"),
            last_login=row.get("last_login"),
            is_active=bool(row.get("is_active", True)),
        )

class SessionToken:
    """Session token model"""
    
    def __init__(
        self,
        token: str,
        user_id: str,
        created_at: Optional[str] = None,
        expires_at: Optional[str] = None,
    ):
        self.token = token
        self.user_id = user_id
        self.created_at = created_at or _now()
        self.expires_at = expires_at
    
    @staticmethod
    def new_token() -> str:
        """Generate new session token"""
        return f"tok_{secrets.token_hex(24)}"
    
    @staticmethod
    def from_db_row(row: dict) -> SessionToken:
        """Create SessionToken from database row"""
        return SessionToken(
            token=row["token"],
            user_id=row["user_id"],
            created_at=row.get("created_at"),
            expires_at=row.get("expires_at"),
        )

class ChatSession:
    """Chat session model"""
    
    def __init__(
        self,
        id: str,
        user_id: str,
        created_at: Optional[str] = None,
        last_activity: Optional[str] = None,
        state: str = "welcome",
        symptoms_json: str = "[]",
    ):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at or _now()
        self.last_activity = last_activity or _now()
        self.state = state
        self.symptoms_json = symptoms_json
    
    def symptoms(self) -> list[str]:
        """Get symptoms list"""
        return _json_loads(self.symptoms_json) or []
    
    def set_symptoms(self, symptoms: list[str]) -> None:
        """Set symptoms list (deduplicated and sorted)"""
        self.symptoms_json = _json_dumps(sorted(set(symptoms)))
    
    @staticmethod
    def from_db_row(row: dict) -> ChatSession:
        """Create ChatSession from database row"""
        return ChatSession(
            id=row["id"],
            user_id=row["user_id"],
            created_at=row.get("created_at"),
            last_activity=row.get("last_activity"),
            state=row.get("state", "welcome"),
            symptoms_json=row.get("symptoms_json", "[]"),
        )

class ChatMessage:
    """Chat message model"""
    
    def __init__(
        self,
        session_id: str,
        role: str,
        content: str,
        id: Optional[int] = None,
        timestamp: Optional[str] = None,
        data_json: Optional[str] = None,
    ):
        self.id = id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.timestamp = timestamp or _now()
        self.data_json = data_json
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "data": _json_loads(self.data_json) if self.data_json else {},
        }
    
    @staticmethod
    def from_db_row(row: dict) -> ChatMessage:
        """Create ChatMessage from database row"""
        return ChatMessage(
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            id=row.get("id"),
            timestamp=row.get("timestamp"),
            data_json=row.get("data_json"),
        )

class ChatHistory:
    """Chat history model"""
    
    def __init__(
        self,
        id: str,
        user_id: str,
        title: str,
        created_at: Optional[str] = None,
        ended_at: Optional[str] = None,
        duration: str = "N/A",
        symptoms_json: str = "[]",
        predictions_json: str = "[]",
        messages_json: str = "[]",
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.created_at = created_at or _now()
        self.ended_at = ended_at or _now()
        self.duration = duration
        self.symptoms_json = symptoms_json
        self.predictions_json = predictions_json
        self.messages_json = messages_json
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "date": self.created_at.split("T")[0] if self.created_at else "",
            "created_at": self.created_at,
            "ended_at": self.ended_at,
            "duration": self.duration,
            "symptoms": _json_loads(self.symptoms_json) or [],
            "predictions": _json_loads(self.predictions_json) or [],
            "messages": _json_loads(self.messages_json) or [],
        }
    
    @staticmethod
    def from_db_row(row: dict) -> ChatHistory:
        """Create ChatHistory from database row"""
        return ChatHistory(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            created_at=row.get("created_at"),
            ended_at=row.get("ended_at"),
            duration=row.get("duration", "N/A"),
            symptoms_json=row.get("symptoms_json", "[]"),
            predictions_json=row.get("predictions_json", "[]"),
            messages_json=row.get("messages_json", "[]"),
        )

