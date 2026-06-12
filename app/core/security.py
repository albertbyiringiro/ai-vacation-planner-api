from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from sqlalchemy import select
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.core.database import SessionDep
from app.domain.models.user import User

password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode["exp"] = expire

    return jwt.encode(  # type: ignore
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(  # type: ignore
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except InvalidTokenError as exc:
        raise ValueError("Could not validate credentials") from exc


async def authenticate_user(
    session: SessionDep, username: str, password: str
) -> User | None:
    result = await session.execute(select(User).filter_by(username=username))

    user = result.scalar_one_or_none()

    if not user or not user.is_active or user.deleted_at is not None:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
