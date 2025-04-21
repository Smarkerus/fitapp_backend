"""Model GPS API."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GPSPoint(BaseModel):
    session_id: str
    timestamp: datetime
    user_id: int
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    acceleration: Optional[float] = 0.0
    last_entry: Optional[bool] = False
