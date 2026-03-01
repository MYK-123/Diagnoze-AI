from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth_db import get_current_admin
from ..database import get_db
from ..db_models import ChatHistory, User
from ..models.responses import success_response, list_response

router = APIRouter()

@router.get("/users", summary="Get all users")
async def get_all_users(
    admin: dict = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get list of all users (admin only)"""
    q = select(User)
    users_list = db.scalars(q).all()

    filtered = users_list
    if search:
        s = search.lower()
        filtered = [
            u
            for u in filtered
            if s in (u.email or "").lower()
            or s in (u.first_name or "").lower()
            or s in (u.last_name or "").lower()
        ]
    if account_type:
        filtered = [u for u in filtered if u.account_type == account_type]

    filtered.sort(key=lambda u: u.created_at or datetime.min, reverse=True)
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    page_rows = filtered[start:end]

    return list_response(items=[u.to_public_dict() for u in page_rows], total=total, page=page, limit=limit)

@router.put("/users/{user_id}", summary="Update user")
async def update_user(
    user_id: str,
    update_data: dict,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update user information (admin only)"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in (update_data or {}).items():
        if value is None:
            continue
        if hasattr(user, key):
            setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return success_response(user.to_public_dict(), "User updated successfully")

@router.delete("/users/{user_id}", summary="Delete user")
async def delete_user(user_id: str, admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Delete user (admin only)"""
    # Don't allow self-deletion
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return success_response(message="User deleted successfully")

@router.get("/analytics", summary="Get system analytics")
async def get_analytics(admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get system analytics (admin only)"""
    users = db.scalars(select(User)).all()
    total_users = len(users)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = len([u for u in users if u.last_login and u.last_login > week_ago])

    chats = db.scalars(select(ChatHistory)).all()
    total_chats = len(chats)
    today = datetime.utcnow().date()
    chats_today = len([c for c in chats if c.created_at and c.created_at.date() == today])
    
    # Common symptoms (dummy data)
    common_symptoms = [
        {"symptom": "Headache", "count": 45},
        {"symptom": "Fever", "count": 32},
        {"symptom": "Cough", "count": 28},
        {"symptom": "Fatigue", "count": 25},
        {"symptom": "Nausea", "count": 18}
    ]
    
    # Common diseases (dummy data)
    common_diseases = [
        {"disease": "Viral Infection", "count": 38, "avg_confidence": 76},
        {"disease": "Migraine", "count": 32, "avg_confidence": 82},
        {"disease": "Allergy", "count": 24, "avg_confidence": 68},
        {"disease": "Sinusitis", "count": 19, "avg_confidence": 71},
        {"disease": "Tension Headache", "count": 15, "avg_confidence": 74}
    ]
    
    # System health
    system_health = {
        "api_status": "healthy",
        "database_status": "connected",
        "response_time_avg": "120ms",
        "error_rate": "0.2%",
        "uptime": "99.8%",
        "last_updated": datetime.now().isoformat()
    }
    
    return success_response({
        "total_users": total_users,
        "active_users": active_users,
        "total_chats": total_chats,
        "chats_today": chats_today,
        "common_symptoms": common_symptoms,
        "common_diseases": common_diseases,
        "system_health": system_health,
        "timestamp": datetime.now().isoformat()
    })

@router.get("/logs", summary="Get system logs")
async def get_logs(
    admin: dict = Depends(get_current_admin),
    action: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """Get system logs (admin only)"""
    # Logs are not persisted yet in SQLite for this demo.
    items: list[dict] = []
    return list_response(items=items, total=0, page=page, limit=limit)

