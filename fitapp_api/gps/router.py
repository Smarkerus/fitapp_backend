from fastapi import APIRouter, HTTPException
from fitapp_api.gps.models import GPSPoint
from fitapp_api.users.models import User
from fitapp_api.users.router import get_current_user
from fitapp_api.misc import insert_gps_points_to_db, get_gps_points_by_trip_id
from fitapp_api.gps.utils import get_session_ids_by_user_id
from fastapi import Depends


gps_router = APIRouter()

# Endpointy
@gps_router.post("/", status_code=200)
async def insert_gps_points(points: list[GPSPoint], current_user: User = Depends(get_current_user)) -> bool:
    for point in points:
        if point.user_id != current_user.id and not current_user.isAdmin:
            raise HTTPException(status_code=403, detail="Brak autoryzacji do uploadu punktów GPS innych uzytkowników!")
    return await insert_gps_points_to_db(points)


@gps_router.get("/points/{session_id}", response_model=list[GPSPoint])
async def get_gps_points_by_session_id(session_id: str, current_user: User = Depends(get_current_user)) -> list[GPSPoint]:
    if session_id not in await get_session_ids_by_user_id(current_user.id):
        raise HTTPException(status_code=403, detail="Brak autoryzacji")
    
    return await get_gps_points_by_trip_id(session_id=session_id)
