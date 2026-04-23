from datetime import datetime
from sqlmodel import SQLModel, Field
from app.domain.models.trip import TripBase, TripStyle


class TripCreate(TripBase):
    pass


class TripUpdate(SQLModel):
    destination: str | None = None
    days: int | None = Field(default=None, ge=1, le=30)
    budget: float | None = Field(default=None, gt=0)
    trip_style: TripStyle | None = None


class TripResponse(TripBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
