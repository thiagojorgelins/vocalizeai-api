FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --no-root


ENTRYPOINT ["./entrypoint.sh"]
