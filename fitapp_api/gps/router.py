from fastapi import APIRouter, HTTPException
from fitapp_api.gps.models import GPSPoint
from fitapp_api.users.models import User
from fitapp_api.users.router import get_current_user
from fitapp_api.misc import insert_gps_points_to_db, get_gps_points_by_trip_id
from fitapp_api.gps.utils import get_session_ids_by_user_id
from fastapi import Depends
from fitapp_api.trips.router import get_trip_summary


gps_router = APIRouter()

# Endpointy
@gps_router.post("/", status_code=200)
async def insert_gps_points(points: list[GPSPoint], current_user: User = Depends(get_current_user)) -> bool:
    sessions_ids_with_last_entry = []
    for point in points:
        if point.user_id != current_user.id and not current_user.isAdmin:
            raise HTTPException(status_code=403, detail="Brak autoryzacji do uploadu punktów GPS innych uzytkowników!")
        if point.last_entry:
            has_last_entry = True
            sessions_ids_with_last_entry.append(point.session_id)
    result = await insert_gps_points_to_db(points)
    if sessions_ids_with_last_entry:
        for session_id in sessions_ids_with_last_entry:
            await get_trip_summary(session_id=session_id, current_user=current_user)
    return result


@gps_router.get("/points/{session_id}", response_model=list[GPSPoint])
async def get_gps_points_by_session_id(session_id: str, current_user: User = Depends(get_current_user)) -> list[GPSPoint]:
    if session_id not in await get_session_ids_by_user_id(current_user.id):
        raise HTTPException(status_code=403, detail="Brak autoryzacji")
    
    return await get_gps_points_by_trip_id(session_id=session_id)
