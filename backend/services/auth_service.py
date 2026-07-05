"""
Authentication Module (Section 4.7 / 4.17.1-4.17.2 of the dissertation).

Handles secure password hashing and JWT-based session tokens so that
administrator credentials are never stored or transmitted in plain text.
"""
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt before it is stored."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Compare a plain-text password against its stored hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str) -> str:
    """Create a signed JWT session token for an authenticated administrator."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> str | None:
    """Return the username stored in a token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None
