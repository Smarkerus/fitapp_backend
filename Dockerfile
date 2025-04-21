FROM python:3.12.7-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
COPY fitapp_api/ /app/fitapp_api/

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

CMD ["uvicorn", "fitapp_api.main:app", "--host", "0.0.0.0", "--port", "8000"]