from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
import json
import secrets

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _now() -> datetime:
    return datetime.utcnow()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _json_loads(value: Optional[str]) -> Any:
    if not value:
        return None
    return json.loads(value)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=18)
    gender: Mapped[str] = mapped_column(String(32), nullable=False, default="prefer_not_to_say")
    account_type: Mapped[str] = mapped_column(String(32), nullable=False, default="user")
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    preferences_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    sessions: Mapped[list["SessionToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "gender": self.gender,
            "account_type": self.account_type,
            "phone": self.phone,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": _json_loads(self.preferences_json) or {},
            "is_active": self.is_active,
        }


class SessionToken(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions")

    @staticmethod
    def new_token() -> str:
        return f"tok_{secrets.token_hex(24)}"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    state: Mapped[str] = mapped_column(String(64), nullable=False, default="welcome")
    symptoms_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    def symptoms(self) -> list[str]:
        return _json_loads(self.symptoms_json) or []

    def set_symptoms(self, symptoms: list[str]) -> None:
        self.symptoms_json = _json_dumps(sorted(set(symptoms)))


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)

    role: Mapped[str] = mapped_column(String(16), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "data": _json_loads(self.data_json) if self.data_json else {},
        }


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    duration: Mapped[str] = mapped_column(String(64), nullable=False, default="N/A")

    symptoms_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    predictions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    messages_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "date": self.created_at.date().isoformat(),
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "duration": self.duration,
            "symptoms": _json_loads(self.symptoms_json) or [],
            "predictions": _json_loads(self.predictions_json) or [],
            "messages": _json_loads(self.messages_json) or [],
        }

