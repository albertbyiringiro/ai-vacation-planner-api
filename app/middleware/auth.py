from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.database import SessionDep
from app.core.security import decode_access_token
from app.domain.models.user import User


PUBLIC_PATHS = {
    "/health",
    "/auth/register",
    "/auth/token",
    "/docs",
    "/redoc",
    "/openapi.json",
}


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    email: str
    is_active: bool
    role: str


class AuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if scope["method"] == "OPTIONS" or is_public_path(scope["path"]):
            await self.app(scope, receive, send)
            return

        token = self._get_bearer_token(Headers(scope=scope).get("Authorization"))
        if token is None:
            await self._unauthorized("Not authenticated")(scope, receive, send)
            return

        try:
            payload = decode_access_token(token)
        except ValueError:
            await self._unauthorized("Could not validate credentials")(
                scope,
                receive,
                send,
            )
            return

        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            await self._unauthorized("Could not validate credentials")(
                scope,
                receive,
                send,
            )
            return

        state = scope.setdefault("state", {})
        state["auth_username"] = username

        await self.app(scope, receive, send)

    @staticmethod
    def _get_bearer_token(authorization: str | None) -> str | None:
        if authorization is None:
            return None

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None

        return token

    @staticmethod
    def _unauthorized(detail: str) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_authenticated_user(
    request: Request,
    session: SessionDep,
) -> AuthenticatedUser:
    user = getattr(request.state, "current_user", None)
    if isinstance(user, AuthenticatedUser):
        return user

    username = getattr(request.state, "auth_username", None)
    if not isinstance(username, str) or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(select(User).filter_by(username=username))
    db_user = result.scalar_one_or_none()

    if db_user is None or db_user.deleted_at is not None or db_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    authenticated_user = AuthenticatedUser(
        id=db_user.id,
        username=db_user.username,
        email=str(db_user.email),
        is_active=db_user.is_active,
        role=db_user.role,
    )
    request.state.current_user = authenticated_user

    return authenticated_user


async def get_authenticated_user_id(
    user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
) -> int:
    return user.id


def is_public_path(path: str) -> bool:
    normalized_path = path.rstrip("/") or "/"
    return normalized_path in PUBLIC_PATHS or normalized_path.startswith("/docs/")


CurrentUser = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]
CurrentUserId = Annotated[int, Depends(get_authenticated_user_id)]
