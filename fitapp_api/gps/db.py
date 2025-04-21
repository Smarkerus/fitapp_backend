import os
from questdb.ingress import Sender
from dotenv import load_dotenv
import asyncpg

load_dotenv()


class GPSDB:
    _instance = None
    _pool = None
    http_conf = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPSDB, cls).__new__(cls)
        return cls._instance

    def get_new_sender(self) -> Sender:
        return Sender.from_conf(self.http_conf)
    
    async def init(self) -> None:
        """Inicjalizuje pulę połączeń do QuestDB."""
        # Interfejs PGWire
        pg_user = os.getenv("QDB_PG_USER", "admin")
        pg_password = os.getenv("QDB_PG_PASSWORD", "quest")
        pg_host = os.getenv("QDB_PG_HOST", "localhost")
        pg_port = int(os.getenv("QDB_PG_PORT", "8812"))
        pg_database = os.getenv("QDB_PG_DB", "qdb")
        # Interfejs HTTP/ILP
        http_host = os.getenv("QDB_HTTP_HOST", "localhost")
        http_port = int(os.getenv("QDB_HTTP_PORT", "9000"))
        http_user = os.getenv("QDB_HTTP_USER", "admin")
        http_password = os.getenv("QDB_HTTP_PASSWORD", "quest")
        self.http_conf = f"http::addr={http_host}:{http_port};username={http_user};password={http_password};"
        
        self._pool = await asyncpg.create_pool(
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
            database=pg_database,
            min_size=1,
            max_size=10
        )

    async def get_connection(self):
        """
        Udostępnia połączenie z QuestDB.
        """
        async with self._pool.acquire() as connection:
            yield connection

gps_db: GPSDB = GPSDB()
