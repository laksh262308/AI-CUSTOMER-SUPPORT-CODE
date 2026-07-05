"""
Relational database models.

These map directly to the tables described in Chapter 3 (Database Design)
of the dissertation:
    Table 3.1 Users
    Table 3.2 Documents
    Table 3.3 Chat History
    Table 3.4 System Logs
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from config import settings

Base = declarative_base()


class User(Base):
    """Table 3.1 Users - administrator accounts."""
    __tablename__ = "users"

    user_id = Column("User_ID", Integer, primary_key=True, autoincrement=True)
    username = Column("Username", String(64), unique=True, nullable=False, index=True)
    password_hash = Column("Password", String(255), nullable=False)
    email = Column("Email", String(120), nullable=True)
    role = Column("Role", String(32), default="admin")
    created_at = Column("Created_At", DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="uploaded_by")


class Document(Base):
    """Table 3.2 Documents - uploaded knowledge-base files."""
    __tablename__ = "documents"

    document_id = Column("Document_ID", Integer, primary_key=True, autoincrement=True)
    user_id = Column("User_ID", Integer, ForeignKey("users.User_ID"), nullable=True)
    file_name = Column("File_Name", String(255), nullable=False)
    file_type = Column("File_Type", String(16), nullable=False)  # PDF / DOCX / TXT
    upload_date = Column("Upload_Date", DateTime, default=datetime.utcnow)
    chunk_count = Column("Chunk_Count", Integer, default=0)
    status = Column("Status", String(32), default="processed")  # processed / failed / processing

    uploaded_by = relationship("User", back_populates="documents")


class ChatSession(Base):
    """Support table for grouping conversations into sessions."""
    __tablename__ = "chat_sessions"

    session_id = Column("Session_ID", String(64), primary_key=True)
    started_at = Column("Started_At", DateTime, default=datetime.utcnow)

    messages = relationship("ChatHistory", back_populates="session")


class ChatHistory(Base):
    """Table 3.3 Chat History - customer/AI conversation records."""
    __tablename__ = "chat_history"

    chat_id = Column("Chat_ID", Integer, primary_key=True, autoincrement=True)
    session_id = Column("Session_ID", String(64), ForeignKey("chat_sessions.Session_ID"))
    user_query = Column("User_Query", Text, nullable=False)
    ai_response = Column("AI_Response", Text, nullable=False)
    timestamp = Column("Timestamp", DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class SystemLog(Base):
    """Table 3.4 System Logs - application activity/audit trail."""
    __tablename__ = "system_logs"

    log_id = Column("Log_ID", Integer, primary_key=True, autoincrement=True)
    event = Column("Event", Text, nullable=False)
    event_time = Column("Event_Time", DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Engine / session setup
# ---------------------------------------------------------------------------
engine = create_engine(
    f"sqlite:///{settings.SQLITE_DB_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
