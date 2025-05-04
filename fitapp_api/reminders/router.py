from fitapp_api.postgres.db import pg_db
from fastapi import APIRouter, Depends, HTTPException, status
from fitapp_api.reminders.models import Reminder, ReminderResponse
from fitapp_api.users.router import get_current_user
from fitapp_api.users.models import User
from sqlmodel import select


reminders_router = APIRouter()

async def get_reminder_by_user_id(user_id: int) -> Reminder | None:
    """Pobierz przypominajkę użytkownika."""
    async for session in pg_db.get_session():
        try:
            statement = select(Reminder).where(Reminder.user_id == user_id)
            results = await session.execute(statement=statement)
            reminders = results.scalars().all()
            return ReminderResponse.from_orm(reminders[0]) if reminders else None

        except Exception as e:
            print(f"Błąd podczas pobierania przypominajki: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Błąd podczas pobierania przypominaki: {str(e)}")

# Endpointy
@reminders_router.get("/reminders")
async def get_reminders(current_user: User = Depends(get_current_user)) -> ReminderResponse | None:
    """Pobierz przypominajkę użytkownika."""
    return await get_reminder_by_user_id(user_id=current_user.id)


@reminders_router.post("/reminders")
async def create_reminder(reminder: Reminder, current_user: User = Depends(get_current_user)) -> ReminderResponse:
    """Utwórz przypominajkę."""
    existing_reminder = await get_reminder_by_user_id(user_id=current_user.id)
    if existing_reminder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Przypominajka już istnieje.")
    
    async for session in pg_db.get_session():
        try:
            reminder.user_id = current_user.id
            session.add(reminder)
            await session.commit()
            await session.refresh(reminder)
            return ReminderResponse.from_orm(reminder)

        except Exception as e:
            print(f"Błąd podczas tworzenia przypominajki: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Błąd podczas tworzenia przypominajki: {str(e)}")


@reminders_router.put("/reminders")
async def update_reminder(reminder: Reminder, current_user: User = Depends(get_current_user)) -> ReminderResponse:
    """Zaktualizuj przypominajkę użytkownika."""
    existing_reminder_response = await get_reminder_by_user_id(user_id=current_user.id)
    if not existing_reminder_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Przypominajka nie istnieje.")

    async for session in pg_db.get_session():
        try:
            statement = select(Reminder).where(Reminder.user_id == current_user.id)
            results = await session.execute(statement=statement)
            existing_reminder = results.scalars().first()

            existing_reminder.min_calories = reminder.min_calories
            existing_reminder.min_distance = reminder.min_distance
            existing_reminder.min_time = reminder.min_time

            session.add(existing_reminder)
            await session.commit()
            await session.refresh(existing_reminder)

            return ReminderResponse.from_orm(existing_reminder)

        except Exception as e:
            print(f"Błąd podczas aktualizacji przypominajki: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Błąd podczas aktualizacji przypominajki: {str(e)}")
