from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Any, Annotated
import jwt
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings
from app.core.database import SessionDep
from app.domain.models.user import User

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


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


async def authenticate_user(
    session: SessionDep, username: str, password: str
) -> User | None:
    result = await session.execute(select(User).filter_by(username=username))

    user = result.scalar_one_or_none()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(  # type: ignore
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username: str | None = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    result = await session.execute(select(User).filter_by(username=username))

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return current_user


CurrentUser = Annotated[User, Depends(get_current_active_user)]


async def get_current_user_id(current_user: CurrentUser):
    if current_user.id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return current_user


UserId = Annotated[int, Depends(get_current_user_id)]
