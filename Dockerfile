FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    postgresql-client \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app/

COPY entrypoint.sh /app
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
