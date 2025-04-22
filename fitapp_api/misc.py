from fitapp_backend.postgres.db import pg_db
from fitapp_backend.gps.db import gps_db
from fitapp_backend.gps.models import GPSPoint
import asyncio
from sqlmodel import select
from fitapp_backend.trips.models import TripSummary, Trip
from fitapp_backend.trips.utils import add_trip_and_trip_summary_to_db
from fastapi import Depends, HTTPException


# Wspólne funkcje pomocnicze - dodane by uniknąć 'circular import'

async def check_if_trip_exists(session_id: str) -> bool:
    async for session in pg_db.get_session():
        statement = select(1).where(Trip.session_id == session_id).limit(1)
        result = await session.execute(statement)
        return result.first() is not None

async def insert_gps_points_to_db(points: list[GPSPoint]) -> bool:
    unique_user_ids = set(point.user_id for point in points)
    if len(unique_user_ids) != 1:
        raise ValueError("Wszystkie punkty GPS muszą mieć tego samego użytkownika.")
    unique_session_ids = set(point.session_id for point in points)
    # Dodanie punktów GPS do bazy danych
    try:
        with gps_db.get_new_sender() as sender:
            for point in points:
                sender.row(
                    table_name="gps_points",
                    symbols={
                        "user_id": str(point.user_id),
                        "session_id": str(point.session_id),
                        "last_entry": str(point.last_entry).lower() if point.last_entry is not None else "false"
                    },
                    columns={
                        "latitude": float(point.latitude),
                        "longitude": float(point.longitude),
                        "acceleration": float(point.acceleration) if point.acceleration is not None else 0.0
                    },
                    at=point.timestamp,
                )
            sender.flush()
    except Exception as e:
        raise RuntimeError(f"Nie udało się dodać do bazy punktów GPS: {str(e)}")
    # Sprawdzanie czy wszystkie session_id istnieją w bazie
    tasks = [asyncio.create_task(check_if_trip_exists(session_id)) for session_id in unique_session_ids]
    checked_session_ids = await asyncio.gather(*tasks)
    # Dodanie tras i ich podsumowań do bazy jeżeli nie istnieją
    input_session_ids_tasks = [asyncio.create_task(add_trip_and_trip_summary_to_db(session_id=session_id, user_id=unique_user_ids.pop() )) for session_id, exists in zip(unique_session_ids, checked_session_ids) if not exists]
    await asyncio.gather(*input_session_ids_tasks)
    return True

async def get_gps_points_by_trip_id(session_id: int) -> list[GPSPoint]:    
    async for session in gps_db.get_connection():
        query = """
                SELECT timestamp, user_id, session_id, last_entry, latitude, longitude, acceleration
                FROM gps_points
                WHERE session_id = $1
                ORDER BY timestamp
            """
            # Wykonanie zapytania z parametrem
        result = await session.fetch(query, session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Brak punktów GPS dla tej sesji")
        points = [GPSPoint(**row) for row in result]

    return points
