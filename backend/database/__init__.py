"""Database package: SQLite models and initialization helpers."""
from database.models import init_db, get_db, SessionLocal, User, Document, ChatSession, ChatHistory, SystemLog
from services.auth_service import hash_password
from config import settings


def seed_default_admin():
    """
    Creates the default administrator account on first run, using the
    credentials supplied in the .env file (DEFAULT_ADMIN_USERNAME /
    DEFAULT_ADMIN_PASSWORD). Safe to call every startup - it only inserts
    a row if no administrator account exists yet.
    """
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
        if existing:
            return
        admin = User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            email=settings.DEFAULT_ADMIN_EMAIL,
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"[startup] Default administrator created: {settings.DEFAULT_ADMIN_USERNAME}")
    finally:
        db.close()
