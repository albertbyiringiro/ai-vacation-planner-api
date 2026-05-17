from datetime import datetime, timezone
from typing import Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class ItineraryBase(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=False)
    data: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))


class Itinerary(ItineraryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": "CURRENT_TIMESTAMP",
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )
