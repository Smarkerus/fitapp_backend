from enum import Enum

class TripActivity(Enum):
	RUNNING: 1
	CYCLING: 2
	WALKING: 3
	CLIMBING: 4
	DIVING: 5
	SWIMMING: 6
	OTHER: 7

class BurnedCaloriesRatio(Enum):
    RUNNING = 1.2
    CYCLING = 1.0
    WALKING = 0.8
    CLIMBING = 1.5
    DIVING = 0.9
    SWIMMING = 1.1
    OTHER = 1.0 
