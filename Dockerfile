FROM python:3.12.7-slim

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev --no-interaction --no-ansi && \
    pip uninstall -y poetry && \
    rm -rf /root/.cache/pypoetry

COPY fitapp_api/ /app/fitapp_api/
COPY serviceAccountKey.json /app/serviceAccountKey.json

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

CMD ["uvicorn", "fitapp_api.main:app", "--host", "0.0.0.0", "--port", "8000"]