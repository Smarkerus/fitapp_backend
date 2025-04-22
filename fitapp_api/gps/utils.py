from fitapp_api.gps.db import gps_db
from asyncpg.exceptions._base import UnknownPostgresError

# Funkcje pomocnicze
async def get_session_ids_by_user_id(user_id: str) -> list[str]:
    query = f"SELECT session_id from gps_points WHERE user_id ilike '{user_id}' GROUP BY session_id"
    try:
        async for connection in gps_db.get_connection():
            results = await connection.fetch(query)
        return [str(row[0]) for row in results]
    except UnknownPostgresError as e:
        return []

