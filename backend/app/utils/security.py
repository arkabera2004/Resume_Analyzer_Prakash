"""Password hashing and JWT helpers."""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Create a JWT whose `sub` claim is the user id (as a string)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.jwt_expire_minutes
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Decode a JWT and return the subject (user id). Raises JWTError if invalid/expired."""
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    subject = payload.get("sub")
    if subject is None:
        raise JWTError("Token missing subject")
    return subject
