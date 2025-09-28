# backend/src/core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from .settings import get_settings
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    sub: Optional[str] = None


def _prepare_password(password: str) -> bytes:
    """
    Prepare password for bcrypt by handling length limits.
    Bcrypt has a 72-byte limit, so we pre-hash longer passwords with SHA256.
    """
    password_bytes = password.encode("utf-8")

    # If password is longer than 72 bytes, pre-hash it
    if len(password_bytes) > 72:
        # Use SHA256 to create a fixed-length hash, then encode as hex
        return hashlib.sha256(password_bytes).hexdigest().encode("utf-8")

    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = _prepare_password(plain_password)
    return pwd_context.verify(password_bytes, hashed_password)


def get_password_hash(password: str) -> str:
    password_bytes = _prepare_password(password)
    return pwd_context.hash(password_bytes)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[uuid.UUID]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return uuid.UUID(user_id)
    except JWTError:
        return None
