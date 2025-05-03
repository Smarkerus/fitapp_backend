from fitapp_api.postgres.db import pg_db
from fastapi import APIRouter, Depends, HTTPException, status
from fitapp_api.users.router import get_current_user
from fitapp_api.users.models import User
from fitapp_api.statistics.models import StatisticsRequest, StatisticsResponse, StatisticActivity
from sqlalchemy.orm import selectinload
from fitapp_api.trips.models import Trip, TripSummary
from sqlmodel import select
from fitapp_api.trips.enums import TripActivity


statistics_router = APIRouter()

def split_trips_into_activities(trips: list[Trip]) -> dict[TripActivity, list[Trip]]:
    activities = {activity: [] for activity in TripActivity}
    for trip in trips:
        if trip.summary and trip.summary.activity in activities:
            activities[trip.summary.activity].append(trip)
    return activities

def generate_statistics_for_trips(trips: list[Trip]) -> StatisticsResponse:
    total_distance = sum(list(map(lambda trip: trip.summary.distance or 0.0, trips)))
    total_time = sum(list(map(lambda trip: trip.summary.duration or 0.0, trips)))
    total_calories_burned = sum(list(map(lambda trip: trip.summary.calories_burned or 0.0, trips)))
    average_speed = total_distance / (total_time / 3600) if total_time > 0 else 0.0

    trips_by_activity = split_trips_into_activities(trips)
    activities: list[StatisticActivity] = []
    for activity, _trips in trips_by_activity.items():
        if _trips:
            distance = sum(trip.summary.distance or 0.0 for trip in _trips)
            time = sum(trip.summary.duration or 0.0 for trip in _trips)
            calories_burned = sum(trip.summary.calories_burned or 0.0 for trip in _trips)
            count = len(_trips)
            activities.append(StatisticActivity(
                activity=activity,
                distance=distance,
                time=time,
                calories_burned=calories_burned,
                count=count
            ))
    
    most_liked_activity = max(activities, key=lambda x: x.count) if activities else None

    return StatisticsResponse(
        user_id=trips[0].user_id,
        average_speed=average_speed,
        total_distance=total_distance,
        total_time=total_time,
        total_calories_burned=total_calories_burned,
        activities=activities,
        most_liked_activity=most_liked_activity.activity if most_liked_activity else None
    )

# Endpointy
@statistics_router.post("/statistics")
async def get_statistics(request: StatisticsRequest, current_user: User = Depends(get_current_user)) -> StatisticsResponse | None:
    if request.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień do przeglądania statystyk tego użytkownika.")

    start_time_naive = request.start_time.replace(tzinfo=None)
    end_time_naive = request.end_time.replace(tzinfo=None)

    async for session in pg_db.get_session():
        try:
            statement = (
                select(Trip)
                .join(TripSummary, Trip.id == TripSummary.trip_id)
                .where(
                    Trip.user_id == request.user_id,
                    TripSummary.start_time >= start_time_naive,
                    TripSummary.end_time <= end_time_naive
                )
                .options(selectinload(Trip.summary))
            )
            
            results = await session.execute(statement)
            trips = results.scalars().all()
            
            if not trips:
                return StatisticsResponse(
                    user_id=request.user_id,
                    average_speed=0.0,
                    total_distance=0.0,
                    total_time=0,
                    total_calories_burned=0.0,
                    activities=[],
                    most_liked_activity=None,
                )

        except Exception as e:
            print(f"Błąd podczas pobierania statystyk: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Błąd podczas pobierania statystyk: {str(e)}")

    return generate_statistics_for_trips(trips=trips)
