"""Modele Tripów dla FitApp."""
from fitapp_api.gps.models import GPSPoint
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TripSummary(SQLModel, table=True):
    trip_id: int = Field(foreign_key="trip.id", primary_key=True)
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    distance: Optional[float] = None
    calories_burned: Optional[float] = None
    trip: "Trip" = Relationship(back_populates="summary")

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    user_id: int
    summary: TripSummary = Relationship(back_populates="trip")

class TripResponse(BaseModel):
    session_id: str
    summary: TripSummary
    points: list[GPSPoint]

    @classmethod
    def from_trip(cls, trip: Trip, points: list[GPSPoint])-> "TripResponse":
        return cls(
            session_id=trip.session_id,
            summary=trip.summary,
            points=points,
        )
