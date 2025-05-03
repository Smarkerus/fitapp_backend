"""Modele Statystyk dla FitApp API."""
from pydantic import BaseModel, Field
from datetime import datetime
from fitapp_api.trips.enums import TripActivity
from typing import Optional

class StatisticsRequest(BaseModel):
	user_id: int = Field(ge=0, le=1000000, description="ID użytkownika")
	start_time: datetime = Field(description="Początek zakresu czasu")
	end_time: datetime = Field(description="Koniec zakresu czasu")


class StatisticActivity(BaseModel):
	activity: TripActivity = Field(description="Typ aktywności")
	distance: float = Field(ge=0, description="Dystans w km")
	time: float = Field(ge=0, le=10000, description="Czas w godzinach")
	calories_burned: float = Field(ge=0, description="Liczba spalonych kalorii")
	count: int = Field(ge=0, le=10000, description="Liczba wystąpień aktywności")


class StatisticsResponse(BaseModel):
	user_id: int = Field(ge=1, le=1000000, description="ID użytkownika")
	average_speed: float = Field(ge=0, description="Średnia prędkość w km/h")
	total_distance: float = Field(ge=0, description="Całkowity dystans w km")
	total_time: float = Field(ge=0, description="Całkowity czas w sekundach")
	total_calories_burned: float = Field(ge=0, description="Całkowita liczba spalonych kalorii")
	activities: list[StatisticActivity] = Field(description="Lista aktywności")
	most_liked_activity: Optional[TripActivity] = Field(description="Najbardziej lubiana aktywność")
