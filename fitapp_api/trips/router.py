from fastapi import APIRouter, Depends, HTTPException, status
from fitapp_api.trips.models import Trip, TripResponse
from fitapp_api.trips.utils import calculate_trip_metrics
from fitapp_api.trips.enums import TripActivity
from fitapp_api.postgres.db import pg_db
from fitapp_api.gps.db import gps_db
from fitapp_api.users.router import get_current_user
from fitapp_api.users.models import User
from fitapp_api.gps.router import get_session_ids_by_user_id
from sqlmodel import select
from sqlalchemy.orm import selectinload
from fitapp_api.misc import get_gps_points_by_trip_id


trip_router = APIRouter()

# Endpointy
@trip_router.get("/trips_list/")
async def get_trips_by_user_id(current_user: User = Depends(get_current_user)) -> list[str]:
    trips_ids: list[str] = await get_session_ids_by_user_id(current_user.id)
    sorted_trips_ids: list[str] = sorted(trips_ids, key=lambda x: int(x.split('_')[0]), reverse=True)
    return sorted_trips_ids

@trip_router.get("/activity_types")
async def get_activity_types(current_user: User = Depends(get_current_user)) -> dict[str, int]:
    return {activity.name: activity.value for activity in TripActivity}

@trip_router.get("/trips/{session_id}")
async def get_trip_summary(session_id: str, current_user: User = Depends(get_current_user)) -> TripResponse:
    async for session in pg_db.get_session():
        statement = select(Trip).options(selectinload(Trip.summary)).where(Trip.session_id == session_id)
        result = await session.execute(statement)
        trip = result.scalars().first()

        # Sprawdzanie, czy podróż/trasa istnieje
        if not trip:
            raise HTTPException(status_code=404, detail="Nie znaleziono podróży!")

        # Sprawdzanie uprawnień
        if trip.user_id != current_user.id and not current_user.isAdmin:
            raise HTTPException(status_code=403, detail="Brak autoryzacji do przeglądania tej podróży!")

        # Pobieranie punktów GPS
        points = await get_gps_points_by_trip_id(session_id=session_id)

        # Sprawdzanie czy istnieje podsumowanie
        if not trip.summary:
            trip_summary, add_to_db = calculate_trip_metrics(trip_id=trip.id, session_id=session_id, points=points)

            trip.summary = trip_summary

            if add_to_db:
                try:
                    session.add(trip)
                    await session.commit()
                    await session.refresh(trip, attribute_names=["summary"])
                except Exception as e:
                    await session.rollback()
                    raise HTTPException(status_code=500, detail=f"Błąd zapisu do bazy danych: {str(e)}")

        return TripResponse.from_trip(trip=trip,
                                      points=points)
