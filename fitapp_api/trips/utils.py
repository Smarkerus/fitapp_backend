from fitapp_api.gps.models import GPSPoint
from fitapp_api.postgres.db import pg_db
from fitapp_api.trips.models import TripSummary, Trip
from fitapp_api.trips.enums import TripActivity, BurnedCaloriesRatio
from typing import Tuple
from haversine import haversine, Unit


# Funkcje pomocnicze

EARTH_RADIUS = 6371.0


async def add_trip_and_trip_summary_to_db(
    session_id: str,
    user_id: int,
    summary_data: dict = {},
):
    """Funkcja do dodawania trasy i podsumowania do bazy danych"""
    async for session in pg_db.get_session():
        trip = Trip(session_id=session_id, user_id=user_id)
        session.add(trip)
        await session.commit()
        await session.refresh(trip)

        if summary_data:
            trip_summary = TripSummary(
                trip_id=trip.id,
                session_id=session_id,
                **summary_data
            )
            session.add(trip_summary)
            await session.commit()
            await session.refresh(trip)

        return trip

def calculate_trip_metrics(trip_id: int, session_id: str, points: list[GPSPoint]) -> Tuple[TripSummary, bool]:
    # TODO: Dodać uzależneinie od masy użytkownika
    """Funkcja do obliczania podsumowania trasy na podstawie punktów GPS."""

    if len(points) < 2:
        return TripSummary(
            trip_id=trip_id,
            session_id=session_id,
            start_time=points[0].timestamp if points else None,
            end_time=None,
            duration=None,
            distance=None,
            calories_burned=None
        ), False

    activity: TripActivity = points[0].activity

    # Sortowanie punktów GPS według czasu
    sorted_points = sorted(points, key=lambda p: p.timestamp)
    start_time = sorted_points[0].timestamp
    end_time = sorted_points[-1].timestamp if len(sorted_points) > 1 else None
    duration = (end_time - start_time).total_seconds() if end_time else None

    end_trip = sorted_points[-1].last_entry

    distance = 0.0
    for i in range(1, len(sorted_points)):
        distance += haversine(
            (sorted_points[i-1].latitude, sorted_points[i-1].longitude),
            (sorted_points[i].latitude, sorted_points[i].longitude),
            unit=Unit.METERS
        )

    calories_burned = distance * BurnedCaloriesRatio.get_ratio(activity=activity) * 50.0 / 1000.0 if distance > 0 else 0

    # Jeżeli trasa nie zakończyła sie, to podsumowanie nie ma pola end_time
    if end_trip:
        final_end_time = sorted_points[-1].timestamp
    else:
        final_end_time = None

    return (TripSummary(
            trip_id=trip_id,
            session_id=session_id,
            start_time=start_time,
            end_time=final_end_time,
            duration=duration,
            distance=distance,
            calories_burned=calories_burned,
            activity=activity,
        ), end_trip)
