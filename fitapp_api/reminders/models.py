"""Model Przypominajki dla FitApp API."""
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    min_calories: Optional[float] = Field(ge=0, description="Minimalna liczba spalonych kalorii", default=None)
    min_distance: Optional[float] = Field(ge=0, description="Minimalny dystans w m", default=None)
    min_time: Optional[float] = Field(ge=0, description="Minimalny czas w sekundach", default=None)

class ReminderResponse(BaseModel):
    id: int
    user_id: int
    min_calories: Optional[float]
    min_distance: Optional[float]
    min_time: Optional[float]

    @classmethod
    def from_orm(cls, obj: Reminder) -> "ReminderResponse":
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            min_calories=obj.min_calories,
            min_distance=obj.min_distance,
            min_time=obj.min_time
        )
