from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.domain.models.itinerary import Itinerary
from app.domain.models.trip import Trip
from app.application.schemas.itinerary import ItineraryCreate, ItineraryUpdate


class ItineraryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_own_trip(self, trip_id: int, user_id: int) -> Trip:
        result = await self.session.execute(
            select(Trip).where(
                Trip.id == trip_id,
                Trip.user_id == user_id,
                Trip.deleted_at == None,
            )
        )
        trip = result.scalar_one_or_none()
        if trip is None:
            raise KeyError("Trip not found or access denied")
        return trip

    async def _get_own_itinerary(self, itinerary_id: int, user_id: int) -> Itinerary:
        result = await self.session.execute(
            select(Itinerary).where(Itinerary.id == itinerary_id)
        )

        itinerary = result.scalar_one_or_none()
        if itinerary is None:
            raise KeyError("Itinerary not found")
        await self._get_own_trip(itinerary.trip_id, user_id)
        return itinerary
