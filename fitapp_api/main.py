from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fitapp_api.users.router import user_router
from fitapp_api.gps.router import gps_router
from fitapp_api.trips.router import trip_router
from fitapp_api.postgres.db import pg_db
from fitapp_api.gps.db import gps_db
from fitapp_api.statistics.router import statistics_router
from fitapp_api.reminders.router import reminders_router

app = FastAPI()

app.add_event_handler("startup", pg_db.init)
app.add_event_handler("startup", gps_db.init)
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(gps_router, prefix="/gps", tags=["gps"])
app.include_router(trip_router, prefix="/trips", tags=["trips"])
app.include_router(statistics_router, prefix="/statistics", tags=["statistics"])
app.include_router(reminders_router, prefix="/reminders", tags=["reminders"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8081", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FitApp API Strona Startowa"}