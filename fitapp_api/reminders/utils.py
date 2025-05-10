from fitapp_api.postgres.db import pg_db
from fitapp_api.reminders.models import Reminder
from fitapp_api.users.models import User, UserFcmID
from fitapp_api.statistics.router import get_statistics_for_user_in_time_range
from sqlalchemy import select, or_
from pyfcm import FCMNotification
from dotenv import load_dotenv
import os
load_dotenv()
import asyncio
from datetime import datetime, date


FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_API_KEY_FILENAME = os.getenv("FIREBASE_API_KEY_FILENAME")

class FCMNotifier:
    """Klasa do wysyłania powiadomień FCM."""

    def __init__(self, api_key_filename: str = FIREBASE_API_KEY_FILENAME, project_id: str = FIREBASE_PROJECT_ID) -> None:
        self.push_notifier = FCMNotification(api_key_filename, project_id)

    async def send_notification(self, title: str, body: str, device_token: str) -> None:
        """Wysyłanie powiadomienia FCM."""
        print(f"Wysyłanie powiadomienia FCM do {device_token}")
        result = self.push_notifier.notify(fcm_token=device_token, notification_title=title, notification_body=body)
        print(f"Wynik wysyłania powiadomienia: {result} dla tokenu {device_token}")

push_notifier = FCMNotifier()

async def create_fcm_push_reminders() -> None:
    """Asynchroniczne tworzenie przypominajek w postaci powiadomień Push (Firebase Cloud Messaging)."""

    user_ids = {}

    async for session in pg_db.get_session():
        try:
            select_statement = select(
                User.id,
                UserFcmID.fcm_push_token,
                Reminder
            ).join(
                UserFcmID, UserFcmID.user_id == User.id
            ).join(
                Reminder, Reminder.user_id == User.id
            ).where(
                or_(
                    Reminder.min_calories != None,
                    Reminder.min_distance != None,
                    Reminder.min_time != None
                ),
                UserFcmID.fcm_push_token != None
            )

            result = await session.execute(select_statement)
            for row in result.all():
                user_id, fcm_token, reminder = row
                if user_id not in user_ids:
                    user_ids[user_id] = {
                        "token": fcm_token,
                        "reminder": reminder
                    }

        except Exception as e:
            print(f"Błąd: {e}")

        if user_ids:
            print(f"Użytkownicy z przypominajkami i tokenami FCM: {user_ids}")
            tasks = []
            start_time = datetime.combine(date.today(), datetime.min.time())
            end_time = datetime.now()
            for user_id in user_ids:
                tasks.append(asyncio.create_task(get_statistics_for_user_in_time_range(user_id, start_time, end_time)))
            results = await asyncio.gather(*tasks)
            notification_tasks = []
            for user_id, statistics in zip(user_ids, results):
                print(f"Statystyki dla użytkownika {user_id}: {statistics} {user_ids[user_id]}")
                reminder = user_ids[user_id]["reminder"]
                token = user_ids[user_id]["token"]
                met_conditions = all((
                    (statistics.total_calories_burned >= reminder.min_calories),
                    (statistics.total_distance >= reminder.min_distance),
                    (statistics.total_time >= reminder.min_time)
                ))
                if met_conditions:
                    title = "Gratulacje!"
                    body = "Wszystko jest ok! Osiągnąłeś swoje cele na dziś!"
                    notification_tasks.append(push_notifier.send_notification(title, body, token))
                else:
                    title = "Nie osiągnięto celów"
                    body = "Nie osiągnąłeś jeszcze swoich celów na dziś. Nie poddawaj się!"
                    notification_tasks.append(push_notifier.send_notification(title, body, token))
            await asyncio.gather(*notification_tasks)
            print("Powiadomienia FCM zostały wysłane.")
        else:
            print("Brak użytkowników z przypominajkami i tokenami FCM.")
