from datetime import datetime
from typing import Any
from pydantic import field_validator
from sqlmodel import SQLModel


class ItineraryDay(SQLModel):
    day: int
    activities: list[str]

    @field_validator("day")
    @classmethod
    def day_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("day must be >= 1")
        return v

    @field_validator("activities")
    @classmethod
    def activities_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("activities list must not be empty")
        return v


class ItineraryCreate(SQLModel):
    name: str | None = None
    days: list[ItineraryDay]


class ItineraryUpdate(SQLModel):
    name: str | None = None
    days: list[ItineraryDay] | None = None


class ItineraryResponse(SQLModel):
    id: int
    trip_id: int
    name: str | None
    is_active: bool
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime
