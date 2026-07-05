"""
Chatbot APIs (Section 4.15.2):
    POST /chat        Submit customer query
    GET  /history      Retrieve conversation history
    GET  /session      Retrieve active chat session
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.models import get_db, ChatHistory, ChatSession
from models.schemas import ChatRequest, ChatResponse, HistoryItem
from rag.pipeline import retrieve_context, build_prompt
from services.ai_service import generate_response, post_process_response
from chatbot.conversation_service import get_conversation_history, save_chat, ensure_session

router = APIRouter(tags=["Chatbot"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    ensure_session(db, payload.session_id)

    # 1. Retrieve relevant business-document context (Semantic Search Module)
    context, matches = retrieve_context(query)

    # 2. Build the prompt combining query + retrieved context + recent history
    history = get_conversation_history(payload.session_id)
    prompt = build_prompt(query, context, history)

    # 3. Generate the AI response (AI Response Generation Module)
    raw_response = generate_response(prompt)
    final_response = post_process_response(raw_response)

    # 4. Persist the exchange (Conversation Management Module)
    save_chat(db, payload.session_id, query, final_response)

    return ChatResponse(status="success", response=final_response, timestamp=datetime.utcnow())


@router.get("/history", response_model=list[HistoryItem])
def get_history(session_id: str = Query(...), db: Session = Depends(get_db)):
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.timestamp.asc())
        .all()
    )
    return [
        HistoryItem(user_query=r.user_query, ai_response=r.ai_response, timestamp=r.timestamp)
        for r in records
    ]


@router.get("/session")
def get_session(session_id: str = Query(...), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session.session_id, "started_at": session.started_at}
