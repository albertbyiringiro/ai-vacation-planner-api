from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User
from app.application.schemas.user import UserCreate
from app.core.security import hash_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        existing = await self.session.execute(
            select(User).filter_by(username=user_data.username)
        )

        if existing.scalar_one_or_none():
            raise ValueError(f"Username '{user_data.username}' is already taken")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).filter_by(username=username))

        return result.scalar_one_or_none()
