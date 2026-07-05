"""
Application entry point for the AI-Based Customer Experience Solution backend.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Interactive API documentation is automatically available at:
    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, seed_default_admin
from api import auth_routes, chat_routes, document_routes, dashboard_routes

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Based Customer Experience Solution using Retrieval-Augmented Generation.",
    version="1.0.0",
)

# CORS - only the configured frontend origin may call these APIs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    seed_default_admin()


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(document_routes.router)
app.include_router(dashboard_routes.router)
