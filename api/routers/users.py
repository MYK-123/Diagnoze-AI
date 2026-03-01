from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..auth_db import get_current_user
from ..database import get_db
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
    db: Session = Depends(get_db),
):
    """Update user profile"""
    db_user = db.get(User, user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_user, field, getattr(value, "value", value))

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return success_response(db_user.to_public_dict(), "Profile updated successfully")

@router.get("/history", summary="Get chat history")
async def get_history(
    user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get user's chat history"""
    q = select(ChatHistory).where(ChatHistory.user_id == user["id"]).order_by(ChatHistory.created_at.desc())
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    page_rows = db.scalars(q.offset((page - 1) * limit).limit(limit)).all()

    return success_response(
        {
            "chats": [r.to_dict() for r in page_rows],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }
    )

@router.get("/history/{chat_id}", summary="Get chat by ID")
async def get_chat_by_id(chat_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get specific chat by ID"""
    chat = db.get(ChatHistory, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != user["id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return success_response(chat.to_dict())

@router.delete("/history/{chat_id}", summary="Delete chat")
async def delete_chat(chat_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete chat from history"""
    chat = db.get(ChatHistory, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != user["id"] and user.get("account_type") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(chat)
    db.commit()
    return success_response(message="Chat deleted successfully")

@router.get("/stats", summary="Get user statistics")
async def get_user_stats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user statistics and insights"""
    chats = db.scalars(select(ChatHistory).where(ChatHistory.user_id == user["id"])).all()
    total_chats = len(chats)

    week_ago = datetime.utcnow() - timedelta(days=7)
    chats_this_week = len([c for c in chats if c.created_at and c.created_at > week_ago])

    all_symptoms: list[str] = []
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

