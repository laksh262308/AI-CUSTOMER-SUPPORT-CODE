"""
Dashboard APIs (Section 4.15.2):
    GET /dashboard    Retrieve dashboard summary
    GET /analytics    View chatbot statistics
    GET /logs         Retrieve application logs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import get_db, Document, ChatHistory, ChatSession, SystemLog, User
from models.schemas import DashboardSummary
from api.deps import get_current_admin

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_documents = db.query(func.count(Document.document_id)).scalar() or 0
    total_conversations = db.query(func.count(ChatHistory.chat_id)).scalar() or 0
    total_sessions = db.query(func.count(ChatSession.session_id)).scalar() or 0
    recent_documents = (
        db.query(Document).order_by(Document.upload_date.desc()).limit(5).all()
    )

    return DashboardSummary(
        total_documents=total_documents,
        total_conversations=total_conversations,
        total_sessions=total_sessions,
        recent_documents=recent_documents,
    )


@router.get("/analytics")
def analytics(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_conversations = db.query(func.count(ChatHistory.chat_id)).scalar() or 0
    busiest_sessions = (
        db.query(ChatHistory.session_id, func.count(ChatHistory.chat_id).label("messages"))
        .group_by(ChatHistory.session_id)
        .order_by(func.count(ChatHistory.chat_id).desc())
        .limit(5)
        .all()
    )
    return {
        "total_conversations": total_conversations,
        "top_sessions": [{"session_id": s, "messages": m} for s, m in busiest_sessions],
    }


@router.get("/logs")
def get_logs(
    limit: int = Query(50, ge=1, le=500),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    logs = db.query(SystemLog).order_by(SystemLog.event_time.desc()).limit(limit).all()
    return [{"event": l.event, "event_time": l.event_time} for l in logs]
