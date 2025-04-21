from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from dotenv import load_dotenv
import os
from typing import AsyncGenerator

load_dotenv()

class PostgresDB:
    """Singleton do zarządzania połączeniami z bazą PostgreSQL."""
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresDB, cls).__new__(cls)
        return cls._instance

    async def init(self):
        """Inicjalizacja silnika bazy i fabryki sesji."""
        if self._engine is None:
            user = os.getenv("POSTGRES_USER", "user")
            password = os.getenv("POSTGRES_PASSWORD", "password")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "fitapp_db")

            postgres_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
            self._engine = create_async_engine(postgres_url, echo=True)
            self._session_factory = sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
            await self.create_tables()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Metoda do pobierania sesji bazy."""
        if self._session_factory is None:
            await self.init()
        async with self._session_factory() as session:
            yield session

    async def create_tables(self):
        """Stworzenie tabeli w bazie (w przypadku ich braku)."""
        if self._engine is None:
            await self.init()

        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

pg_db = PostgresDB()
