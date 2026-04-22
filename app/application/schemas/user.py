from pydantic import field_validator
from sqlmodel import SQLModel

from app.domain.models.user import UserBase


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*(){}|;:,.<>?/~`" for c in v):
            raise ValueError("Password must contain at least one special character")

        return v


class UserResponse(UserBase):
    id: int


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
