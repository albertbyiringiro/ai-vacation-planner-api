from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.trip import Trip
from app.application.schemas.trip import TripCreate, TripUpdate


class TripService:
    def __init__(self, session: AsyncSession, user_id: int) -> None:
        self.session = session
        self.user_id = user_id

    async def _get_own_trip(self, trip_id: int) -> Trip:
        trip = await self.session.get(Trip, trip_id)

        if trip is None or trip.deleted_at is not None:
            raise KeyError(f"Trip {trip_id} not found")

        if trip.user_id != self.user_id:
            raise PermissionError(f"Trip {trip_id} does not belong to you")

        return trip

    async def create(self, trip_data: TripCreate) -> Trip:
        trip = Trip.model_validate(trip_data, update={"user_id": self.user_id})
        self.session.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip

    async def list_for_user(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Trip]:
        stmt = (
            select(Trip)
            .where(Trip.user_id == self.user_id, Trip.deleted_at.is_(None))  # type: ignore
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, trip_id: int) -> Trip:
        return await self._get_own_trip(trip_id)

    async def patch(self, trip_id: int, trip_data: TripUpdate) -> Trip:
        trip = await self._get_own_trip(trip_id)
        trip.sqlmodel_update(trip_data.model_dump(exclude_unset=True))
        self.session.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip

    async def delete(self, trip_id: int) -> None:
        trip = await self._get_own_trip(trip_id)
        trip.deleted_at = datetime.now(timezone.utc)
        self.session.add(trip)
        await self.session.commit()
