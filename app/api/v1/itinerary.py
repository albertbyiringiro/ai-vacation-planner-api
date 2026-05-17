from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.database import SessionDep
from app.core.security import UserId
from app.application.schemas.itinerary import (
    ItineraryCreate,
    ItineraryResponse,
    ItineraryUpdate,
)
from app.application.services.itinerary import ConflictError, ItineraryService

router = APIRouter(tags=["itineraries"])


def get_service(session: SessionDep) -> ItineraryService:
    return ItineraryService(session)


@router.post(
    "/trips/{trip_id}/itineraries",
    response_model=ItineraryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_itinerary(
    trip_id: int,
    body: ItineraryCreate,
    user_id: UserId,
    service: ItineraryService = Depends(get_service),
):
    try:
        return await service.create(trip_id, user_id, body)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/trips/{trip_id}/itineraries",
    response_model=list[ItineraryResponse],
)
async def list_itineraries(
    trip_id: int,
    user_id: UserId,
    active_only: bool = Query(default=False),
    service: ItineraryService = Depends(get_service),
):
    try:
        return await service.list_for_trip(trip_id, user_id, active_only)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/itineraries/{itinerary_id}",
    response_model=ItineraryResponse,
)
async def get_itinerary(
    itinerary_id: int,
    user_id: UserId,
    service: ItineraryService = Depends(get_service),
):
    try:
        return await service.get(itinerary_id, user_id)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/itineraries/{itinerary_id}",
    response_model=ItineraryResponse,
)
async def update_itinerary(
    itinerary_id: int,
    body: ItineraryUpdate,
    user_id: UserId,
    service: ItineraryService = Depends(get_service),
):
    try:
        return await service.update(itinerary_id, user_id, body)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/itineraries/{itinerary_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate_itinerary(
    itinerary_id: int,
    user_id: UserId,
    service: ItineraryService = Depends(get_service),
):
    try:
        await service.activate(itinerary_id, user_id)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/itineraries/{itinerary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_itinerary(
    itinerary_id: int,
    user_id: UserId,
    service: ItineraryService = Depends(get_service),
):
    try:
        await service.delete(itinerary_id, user_id)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
