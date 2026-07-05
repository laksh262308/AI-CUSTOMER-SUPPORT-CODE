"""
Conversation Management (Sections 3.5.7 and 4.14.4).

Maintains lightweight per-session conversation memory so that follow-up
questions can be interpreted within the context of the ongoing chat, and
persists every exchange to the Chat History table for later analysis.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import ChatSession, ChatHistory

# In-memory recent-turn cache per session (kept small; full history lives in SQLite)
_MAX_TURNS_IN_MEMORY = 5
_session_memory: dict[str, list[tuple[str, str]]] = {}


def get_conversation_history(session_id: str) -> str:
    """Return the last few turns of a session formatted as plain text."""
    turns = _session_memory.get(session_id, [])
    return "\n".join(f"Customer: {q}\nAssistant: {a}" for q, a in turns)


def remember_turn(session_id: str, query: str, response: str):
    """Append a turn to the in-memory conversation cache for a session."""
    turns = _session_memory.setdefault(session_id, [])
    turns.append((query, response))
    if len(turns) > _MAX_TURNS_IN_MEMORY:
        del turns[0]


def ensure_session(db: Session, session_id: str):
    """Create the chat session row if it does not already exist."""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id, started_at=datetime.utcnow())
        db.add(session)
        db.commit()
    return session


def save_chat(db: Session, session_id: str, query: str, response: str):
    """Persist a customer/AI exchange to the Chat History table."""
    ensure_session(db, session_id)
    record = ChatHistory(
        session_id=session_id,
        user_query=query,
        ai_response=response,
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    remember_turn(session_id, query, response)
    return record
