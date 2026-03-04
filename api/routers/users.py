from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter
import sqlite3

from db.core import get_db

from ..auth_db import get_current_user
from ..database import Database
from ..db_models import ChatHistory, User
from ..models.responses import success_response, list_response
from ..models.schemas import UserUpdate

router = APIRouter()

@router.get("/profile", summary="Get user profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    return success_response(user)

@router.put("/profile", summary="Update user profile")
async def update_profile(
    update_data: UserUpdate,
    user: dict = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Update user profile"""
    db = Database(conn)
    db_user_row = db.fetch_one("SELECT * FROM users WHERE id = ?", (user["id"],))
    if not db_user_row:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = User.from_db_row(db_user_row)
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if value is not None:
            setattr(db_user, field, value)

    db.execute(
        """
        UPDATE users SET first_name=?, last_name=?, age=?, gender=?, phone=?
        WHERE id=?
        """,
        (db_user.first_name, db_user.last_name, db_user.age, db_user.gender, db_user.phone, db_user.id)
    )
    db.commit()

    return success_response(db_user.to_public_dict(), "Profile updated successfully")

@router.get("/history", summary="Get chat history")
async def get_history(
    user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Get user's chat history"""
    db = Database(conn)
    
    total = db.fetch_scalar(
        "SELECT COUNT(*) FROM chat_history WHERE user_id = ?",
        (user["id"],)
    ) or 0
    
    rows = db.fetch_all(
        """
        SELECT * FROM chat_history WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (user["id"], limit, (page - 1) * limit)
    )
    
    chats = [ChatHistory.from_db_row(row).to_dict() for row in rows]

    return success_response(
        {
            "chats": chats,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }
    )

@router.get("/history/{chat_id}", summary="Get chat by ID")
async def get_chat_by_id(chat_id: str, user: dict = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Get specific chat by ID"""
    db = Database(conn)
    chat_row = db.fetch_one("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
    
    if not chat_row:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = ChatHistory.from_db_row(chat_row)
    
    if chat.user_id != user["id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return success_response(chat.to_dict())

@router.delete("/history/{chat_id}", summary="Delete chat")
async def delete_chat(chat_id: str, user: dict = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Delete chat from history"""
    db = Database(conn)
    chat_row = db.fetch_one("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
    
    if not chat_row:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = ChatHistory.from_db_row(chat_row)
    
    if chat.user_id != user["id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.execute("DELETE FROM chat_history WHERE id = ?", (chat_id,))
    db.commit()
    
    return success_response(message="Chat deleted successfully")

@router.get("/stats", summary="Get user statistics")
async def get_user_stats(user: dict = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
    """Get user statistics and insights"""
    db = Database(conn)
    
    chats_rows = db.fetch_all(
        "SELECT * FROM chat_history WHERE user_id = ?",
        (user["id"],)
    )
    
    chats = [ChatHistory.from_db_row(row) for row in chats_rows]
    total_chats = len(chats)

    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    chats_this_week = len([c for c in chats if c.created_at and c.created_at > week_ago])

    all_symptoms = []
    for c in chats:
        all_symptoms.extend(c.to_dict().get("symptoms", []))

    common_symptoms = Counter(all_symptoms).most_common(5)

    return success_response(
        {
            "total_chats": total_chats,
            "chats_this_week": chats_this_week,
            "common_symptoms": [{"symptom": s, "count": n} for s, n in common_symptoms],
            "accuracy_rate": 87,
            "active_days": min(total_chats, 30),
        }
    )

