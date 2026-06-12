from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import SessionDep
from app.application.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.application.services.trip import TripService
from app.domain.models.trip import Trip
from app.middleware.auth import CurrentUserId

router = APIRouter(prefix="/trips", tags=["trips"])


async def get_trip_service(session: SessionDep, user_id: CurrentUserId) -> TripService:
    return TripService(session, user_id)


TripServiceDep = Annotated[TripService, Depends(get_trip_service)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TripResponse)
async def create_trip(
    trip_data: TripCreate,
    service: TripServiceDep,
) -> Trip:
    return await service.create(trip_data)


@router.get("/", response_model=list[TripResponse])
async def list_trips(
    service: TripServiceDep,
    skip: int = 0,
    limit: int = 10,
) -> list[Trip]:
    return await service.list_for_user(skip, limit)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: int,
    service: TripServiceDep,
) -> Trip:
    try:
        return await service.get(trip_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{trip_id}", response_model=TripResponse)
async def patch_trip(
    trip_id: int,
    trip_data: TripUpdate,
    service: TripServiceDep,
) -> Trip:
    try:
        return await service.patch(trip_id, trip_data)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(trip_id: int, service: TripServiceDep) -> None:
    try:
        await service.delete(trip_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
