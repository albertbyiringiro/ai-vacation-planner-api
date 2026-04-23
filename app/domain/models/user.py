from datetime import datetime, timezone
import enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = None
