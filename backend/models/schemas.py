"""Pydantic models used for request validation and response formatting."""
from datetime import datetime
from pydantic import BaseModel, Field


# --- Authentication -----------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


# --- Chat -----------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    query: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    status: str
    response: str
    timestamp: datetime


class HistoryItem(BaseModel):
    user_query: str
    ai_response: str
    timestamp: datetime


# --- Documents --------------------------------------------------------
class DocumentResponse(BaseModel):
    document_id: int
    file_name: str
    file_type: str
    upload_date: datetime
    chunk_count: int
    status: str


# --- Dashboard ----------------------------------------------------------
class DashboardSummary(BaseModel):
    total_documents: int
    total_conversations: int
    total_sessions: int
    recent_documents: list[DocumentResponse]
