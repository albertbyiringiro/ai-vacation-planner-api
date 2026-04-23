from datetime import datetime, timezone
import enum
from sqlmodel import SQLModel, Field
from sqlalchemy import func


class TripStyle(str, enum.Enum):
    budget = "budget"
    standard = "standard"
    luxury = "luxury"
    family = "family"
    adventure = "adventure"


class TripBase(SQLModel):
    destination: str
    days: int = Field(ge=1, le=30)
    budget: float = Field(gt=0)
    trip_style: TripStyle


class Trip(TripBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
        nullable=False,
    )
    deleted_at: datetime | None = None
