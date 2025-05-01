## Instalacja lokalna i uruchomienie projektu (Python 3 + Poetry)
1.  Upewnij się, że masz zainstalowanego Pythona 3.9+ oraz manager pakietów Pythona `pip`.
2.  Sklonuj repozytorium projektu:

    ```bash
    git clone <adres_repozytorium>
    cd <nazwa_projektu>
    ```
3.  Zainstaluj Poetry (jeżeli jeszcze nie masz):

    ```bash
    python -m pip install poetry
    ```
3. Skonfiguruj Poetry tak, aby tworzył środowisko wirtualne w folderze projektu (zalecane):

    ```bash
    poetry config virtualenvs.in-project true
    ```
 
4.  Zainstaluj zależności projektu za pomocą Poetry:

    ```bash
    poetry install
    ```
5.  Aktywuj stworzone środowisko Pythona:

    Windows:
    ```bash
    .\.venv\Scripts\activate
    ```

    Linux/iOS
    ```bash
    source .venv/bin/activate
    ```

6.  Lokalne uruchomienie aplikacji możliwe będzie po wykonaniu komendy:

    ```bash
    python -m uvicorn fitapp_api.main:app --host 0.0.0.0 --port 8000
    ```

## Uruchomienie lokalne (Docker Compose)

1.  Upewnij się, że masz zainstalowanego Dockera.
2.  Stwórz plik `.env` i wstaw do niego zawartość pliku `.env.example`, dostosuj zmienne środowiskowe:

    Konfiguracja zmiennych środowiskowych w pliku `.env`:

    ```
    PYTHONDONTWRITEBYTECODE=1
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=fitapp_db
    QDB_HTTP_HOST=localhost
    QDB_HTTP_PORT=9000
    QDB_HTTP_USER=questdb
    QDB_HTTP_PASSWORD=questdb
    QDB_PG_HOST=localhost
    QDB_PG_PORT=8812
    QDB_PG_USER=admin
    QDB_PG_PASSWORD=quest
    ```

    *   `PYTHONDONTWRITEBYTECODE`: Wyłącza tworzenie plików `.pyc` (bytecode) przez Pythona.
    *   `POSTGRES_HOST`: Adres hosta serwera PostgreSQL.
    *   `POSTGRES_PORT`: Port serwera PostgreSQL.
    *   `POSTGRES_USER`: Nazwa użytkownika PostgreSQL.
    *   `POSTGRES_PASSWORD`: Hasło użytkownika PostgreSQL.
    *   `POSTGRES_DB`: Nazwa bazy danych PostgreSQL.
    *   `QDB_HTTP_HOST`: Adres hosta QuestDB (interfejs HTTP).
    *   `QDB_HTTP_PORT`: Port interfejsu HTTP QuestDB.
    *   `QDB_HTTP_USER`: Nazwa użytkownika QuestDB (interfejs HTTP).
    *   `QDB_HTTP_PASSWORD`: Hasło użytkownika QuestDB (interfejs HTTP).
    *   `QDB_PG_HOST`: Adres hosta QuestDB (interfejs PostgreSQL).
    *   `QDB_PG_PORT`: Port interfejsu PostgreSQL QuestDB.
    *   `QDB_PG_USER`: Nazwa użytkownika QuestDB (interfejs PostgreSQL).
    *   `QDB_PG_PASSWORD`: Hasło użytkownika QuestDB (interfejs PostgreSQL).

3.  Uruchom kontenery Dockera:

    ```bash
    docker-compose up -d --build
    ```

    Opcja `--build` zbuduje obrazy Docker przed uruchomieniem kontenerów. Możesz pominąć `--build`, jeśli obrazy zostały już zbudowane.

4.  Aplikacja powinna być dostępna pod adresem `http://localhost:8000/`, a jej interfejs można przestudiować również pod adresem `http://localhost:8000/docs`.
